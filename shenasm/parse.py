from collections import namedtuple


from .source import LineOfSource


class Instruction(namedtuple('Instruction', 'source_pos label condition mneumonic args')):

    def replace(self, **kwargs):
        return self._replace(**kwargs)


class Parser(object):

    def __init__(self, issues):
        self._issues = issues

    def parse_lines(self, lines: [LineOfSource]) -> [Instruction]:
        """
        takes a collection of lines and parses them into instructions
        :param lines: the lines to parse
        :return: the resulting instruction list
        """
        return list(
            filter(
                lambda x: x is not None,
                map(
                    self._parse_line,
                    lines
                )
            )
        )

    def _parse_line(self, line: LineOfSource) -> Instruction:
        """
        parses a single line into an assembly instruction
        :param line: the line to parse
        :return: an instruction object parsed from the given line
        """

        text = line.text

        # remove comments
        comment_start = text.find("#")
        if comment_start != -1:
            text = text[:comment_start]
        text = text.strip()

        # empty lines don't need parsing
        if not text:
            return None

        # parse by spaces, the list comprehension is to remove empty strings when double spacing etc is used
        tokens = [token for token in text.split(" ") if token]
        label, condition, mneumonic, args = None, None, None, None
        # label?
        if tokens[0].endswith(":"):
            label = tokens[0]
            tokens = tokens[1:]
        if len(tokens) > 0:
            # conditional?
            if tokens[0] in ('+', '-', '@'):
                condition = tokens[0]
                tokens = tokens[1:]
            if len(tokens) > 0:
                # rest must be mneumonic and args
                mneumonic = tokens[0].lower()
                args = tokens[1:]
        if condition is not None and mneumonic is None:
            self._issues.error(
                line.pos,
                "condition symbol '{}' found with no associated instruction?",
                condition
            )
        return Instruction(line.pos, label, condition, mneumonic, args)
