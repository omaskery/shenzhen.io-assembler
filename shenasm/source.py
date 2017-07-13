import typing
import os


from .errors import IssueLog


class LineOfSource(object):

    def __init__(self, pos, text):
        self._pos = pos
        self._text = text

    @property
    def pos(self):
        return self._pos

    @property
    def text(self):
        return self._text


class SourcePosition(object):

    def __init__(self, file, line):
        self._file = file
        self._line = line

    @property
    def file(self):
        return self._file

    @property
    def line(self):
        return self._line

    def __str__(self):
        return "{}{}".format(
            self.file,
            ":{}".format(self.line) if self.line else ""
        )


def read_lines(issues: IssueLog, file, path: str, included_files: typing.Dict[str, SourcePosition]) -> [LineOfSource]:
    """
    reads all the lines from a file and matches them up with their source position
    :param issues: a collection of issues generated during the assembler's execution
    :param file: the file handle to read lines from
    :param path: the path to the file being read
    :param included_files: a record of what files have been included already (and from where) to prevent include cycles
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
            if len(tokens) < 2:
                issues.error(
                    pos,
                    "include directive expects a parameter: a file path enclosed in quotes"
                )
                continue

            included_path = tokens[1]

            # ensure it is surrounded in quotation marks, it's a bit silly to enforce this
            # in a way... but if you did smarter parsing this could be beneficial
            if not (included_path.startswith('"') and included_path.endswith('"')):
                issues.error(
                    pos,
                    "include directive expects filepath surrounded in quotation marks"
                )
                continue

            # remove quotation marks
            included_path = included_path[1:-1]

            # make path absolute
            if not os.path.isabs(included_path):
                current_folder = os.path.dirname(path)
                included_path = os.path.join(current_folder, included_path)

            # ensure it's a real file
            if not os.path.isfile(included_path):
                issues.error(
                    pos,
                    "include directive specifies invalid file '{}'".format(
                        included_path
                    )
                )
                continue

            # try to open the file, if we can't open it then report an error
            try:
                handle = open(included_path)
            except IOError as io_error:
                issues.error(
                    pos,
                    "error opening included file '{}': {}".format(
                        included_path,
                        io_error
                    )
                )
                continue

            # check for include cycles
            if included_path in included_files:
                issues.error(
                    pos,
                    "include file {} is already included here: {}".format(
                        included_path,
                        included_files[included_path]
                    )
                )
                continue

            included_files[included_path] = pos

            # add all the included lines into our result using recursion
            result.extend(
                read_lines(issues, handle, included_path, included_files)
            )
        # this line looks like a preprocessor directive, but we can't handle it
        elif line.startswith("!"):
            words = line.split()
            directive = words[0][1:]
            issues.warning(
                pos,
                "unknown preprocessor directive '{}'",
                directive
            )
        # this looks like a normal line of source, record it in our results
        else:
            result.append(
                LineOfSource(SourcePosition(path, number), line.strip())
            )
    return result
