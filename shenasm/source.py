from collections import namedtuple
import os


from .errors import AssemblerException


LineOfSource = namedtuple('LineOfSource', 'pos text')


class SourcePosition(namedtuple('SourcePosition', 'file line')):

    def __str__(self):
        return "{}{}".format(
            self.file,
            ":{}".format(self.line) if self.line else ""
        )


def read_lines(file, path: str, included_files: [str]) -> [LineOfSource]:
    """
    reads all the lines from a file and matches them up with their source position
    :param file: the file handle to read lines from
    :param path: the path to the file being read
    :return: a collection of objects describing lines of text and their source position
    """

    result = []
    # read in each line, tagging it with source position information, handling
    # preprocessor directives as we go
    for number, line in enumerate(file.readlines(), start=1):
        pos = SourcePosition(path, number)
        line = line.strip()

        # handle preprocessor logic here (refactor elsewhere? :/)
        if line.startswith("!include"):
            # split the include into its directive and the included path
            tokens = line.split(maxsplit=1)
            if len(tokens) < 1:
                raise AssemblerException(
                    pos,
                    "include directive expects a parameter: a file path enclosed in quotes"
                )
            included_path = tokens[1]
            # ensure it is surrounded in quotation marks, it's a bit silly to enforce this
            # in a way... but if you did smarter parsing this could be beneficial
            if not (included_path.startswith('"') and included_path.endswith('"')):
                raise AssemblerException(
                    pos,
                    "include directive expects filepath surrounded in quotation marks"
                )
            # remove quotation marks
            included_path = included_path[1:-1]

            # make path absolute
            if not os.path.isabs(included_path):
                current_folder = os.path.dirname(path)
                included_path = os.path.join(current_folder, included_path)

            # ensure it's a real file
            if not os.path.isfile(included_path):
                raise AssemblerException(
                    pos,
                    "include directive specifies invalid file '{}'".format(
                        included_path
                    )
                )

            # try to open the file, if we can't open it then report an error
            try:
                handle = open(included_path)
            except IOError as io_error:
                raise AssemblerException(
                    pos,
                    "error opening included file '{}': {}".format(
                        included_path,
                        io_error
                    )
                )

            # check for include cycles
            if included_path in included_files:
                raise AssemblerException(
                    pos,
                    "include file {} is already included here: {}".format(
                        included_path,
                        included_files[included_path]
                    )
                )
            included_files[included_path] = pos

            # add all the included lines into our result using recursion
            result.extend(
                read_lines(handle, included_path, included_files)
            )
        # this line looks like a preprocessor directive, but we can't handle it
        elif line.startswith("!"):
            print("warning [{}]: unknown preprocessor directive '{}'".format(
                pos, line.split(maxsplit=1)[0][1:]
            ))
        # this looks like a normal line of source, record it in our results
        else:
            result.append(
                LineOfSource(SourcePosition(path, number), line.strip())
            )
    return result
