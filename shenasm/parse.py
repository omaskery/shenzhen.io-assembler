import itertools
import typing


from .source import LineOfSource


class Instruction(object):

    def __init__(self, source_pos, label, condition, mnemonic, args):
        self._source_pos = source_pos
        self._label = label
        self._condition = condition
        self._mnemonic = mnemonic
        self._args = args

    @property
    def source_pos(self):
        return self._source_pos

    @property
    def label(self):
        return self._label

    @property
    def condition(self):
        return self._condition

    @property
    def mnemonic(self):
        return self._mnemonic

    @property
    def args(self):
        return self._args

    def replace(self, **kwargs):
        return Instruction(
            kwargs.get("source_pos", self.source_pos),
            kwargs.get("label", self.label),
            kwargs.get("condition", self.condition),
            kwargs.get("mnemonic", self.mnemonic),
            kwargs.get("args", self.args),
        )

    def __str__(self):
        return "{}{}{}{}".format(
            self.label if self.label is not None else ("  " if self.condition is None else ""),
            self.condition + " " if self.condition is not None else "",
            self.mnemonic if self.mnemonic is not None else "",
            " " + " ".join(self.args) if self.args is not None else ""
        )


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
            itertools.chain.from_iterable(
                map(
                    self._parse_line,
                    lines
                )
            )
        )

    def _parse_line(self, line: LineOfSource) -> [Instruction]:
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
            return []

        # parse by spaces, the list comprehension is to remove empty strings when double spacing etc is used
        tokens = [token for token in text.split(" ") if token]
        label, condition, mnemonic, args = None, None, None, None
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
                # rest must be mnemonic and args
                mnemonic = tokens[0].lower()
                args = tokens[1:]
        if condition is not None and mnemonic is None:
            self._issues.error(
                line.pos,
                "condition symbol '{}' found with no associated instruction?",
                condition
            )

        result = [Instruction(line.pos, label, condition, mnemonic, args)]
        if label is not None and mnemonic is not None:
            result = [
                Instruction(line.pos, label, None, None, None),
                Instruction(line.pos, None, condition, mnemonic, args),
            ]

        return result
