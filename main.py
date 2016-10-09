from collections import OrderedDict
from collections import namedtuple
from itertools import zip_longest
import argparse
import typing
import os


ChipInfo = namedtuple('ChipInfo', 'registers memory')
RegisterInfo = namedtuple('RegisterInfo', 'name type')
Symbol = namedtuple('Symbol', 'source_pos name value')
InstructionInfo = namedtuple('InstructionInfo', 'mneumonic argtypes')
LineOfSource = namedtuple('LineOfSource', 'pos text')


class SourcePosition(namedtuple('SourcePosition', 'file line')):

    def __str__(self):
        return "{}{}".format(
            self.file,
            ":{}".format(self.line) if self.line else ""
        )


class Instruction(namedtuple('Instruction', 'source_pos label condition mneumonic args')):

    def replace(self, **kwargs):
        return self._replace(**kwargs)


REG_TYPE_NORMAL = 'normal'
REG_TYPE_SIMPLE = 'simple'
REG_TYPE_XBUS = 'xbus'

INST_ARG_TYPE_REG = 0
INST_ARG_TYPE_INT = 1
INST_ARG_TYPE_LBL = 2
INST_ARG_TYPE_SIMPLE_PIN = 3
INST_ARG_TYPE_XBUS_PIN = 4
INST_ARG_TYPE_NAME = 5

CHIP_TYPE_MC4000 = 'MC4000'
CHIP_TYPE_MC4000X = 'MC4000X'
CHIP_TYPE_MC6000 = 'MC6000'

CHIP_OP_NOP = 'nop'
CHIP_OP_MOV = 'mov'
CHIP_OP_JMP = 'jmp'
CHIP_OP_SLP = 'slp'
CHIP_OP_SLX = 'slx'
CHIP_OP_ADD = 'add'
CHIP_OP_SUB = 'sub'
CHIP_OP_MUL = 'mul'
CHIP_OP_NOT = 'not'
CHIP_OP_DGT = 'dgt'
CHIP_OP_DST = 'dst'
CHIP_OP_TEQ = 'teq'
CHIP_OP_TGT = 'tgt'
CHIP_OP_TLT = 'tlt'
CHIP_OP_TCP = 'tcp'
CHIP_OP_GEN = 'gen'

FAKE_OP_ALIAS = 'alias'
FAKE_OP_CONST = 'const'


INSTRUCTIONS = {
    CHIP_OP_NOP: InstructionInfo(
        mneumonic=CHIP_OP_NOP,
        argtypes=[],
    ),
    CHIP_OP_MOV: InstructionInfo(
        mneumonic=CHIP_OP_MOV,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG],
        ],
    ),
    CHIP_OP_JMP: InstructionInfo(
        mneumonic=CHIP_OP_JMP,
        argtypes=[
            [INST_ARG_TYPE_LBL],
        ],
    ),
    CHIP_OP_SLP: InstructionInfo(
        mneumonic=CHIP_OP_SLP,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_SLX: InstructionInfo(
        mneumonic=CHIP_OP_SLX,
        argtypes=[
            [INST_ARG_TYPE_XBUS_PIN],
        ],
    ),
    CHIP_OP_ADD: InstructionInfo(
        mneumonic=CHIP_OP_ADD,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_SUB: InstructionInfo(
        mneumonic=CHIP_OP_SUB,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_MUL: InstructionInfo(
        mneumonic=CHIP_OP_MUL,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_NOT: InstructionInfo(
        mneumonic=CHIP_OP_NOT,
        argtypes=[],
    ),
    CHIP_OP_DGT: InstructionInfo(
        mneumonic=CHIP_OP_DGT,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_DST: InstructionInfo(
        mneumonic=CHIP_OP_DST,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TEQ: InstructionInfo(
        mneumonic=CHIP_OP_TEQ,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TGT: InstructionInfo(
        mneumonic=CHIP_OP_TGT,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TLT: InstructionInfo(
        mneumonic=CHIP_OP_TLT,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TCP: InstructionInfo(
        mneumonic=CHIP_OP_TCP,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_GEN: InstructionInfo(
        mneumonic=CHIP_OP_GEN,
        argtypes=[
            [INST_ARG_TYPE_SIMPLE_PIN],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
}

VIRTUAL_INSTRUCTIONS = {
    FAKE_OP_ALIAS: InstructionInfo(
        mneumonic=FAKE_OP_ALIAS,
        argtypes=[
            [INST_ARG_TYPE_NAME],
            [INST_ARG_TYPE_REG],
        ]
    ),
    FAKE_OP_CONST: InstructionInfo(
        mneumonic=FAKE_OP_CONST,
        argtypes=[
            [INST_ARG_TYPE_NAME],
            [INST_ARG_TYPE_INT],
        ]
    ),
}


CHIPS = {
    CHIP_TYPE_MC4000: ChipInfo(
        registers=[
            RegisterInfo('null', REG_TYPE_NORMAL),
            RegisterInfo('acc', REG_TYPE_NORMAL),
            RegisterInfo('p0', REG_TYPE_SIMPLE),
            RegisterInfo('p1', REG_TYPE_SIMPLE),
            RegisterInfo('x0', REG_TYPE_XBUS),
            RegisterInfo('x1', REG_TYPE_XBUS),
        ],
        memory=9
    ),
    CHIP_TYPE_MC4000X: ChipInfo(
        registers=[
            RegisterInfo('null', REG_TYPE_NORMAL),
            RegisterInfo('acc', REG_TYPE_NORMAL),
            RegisterInfo('x0', REG_TYPE_XBUS),
            RegisterInfo('x1', REG_TYPE_XBUS),
            RegisterInfo('x2', REG_TYPE_XBUS),
            RegisterInfo('x3', REG_TYPE_XBUS),
        ],
        memory=9
    ),
    CHIP_TYPE_MC6000: ChipInfo(
        registers=[
            RegisterInfo('null', REG_TYPE_NORMAL),
            RegisterInfo('acc', REG_TYPE_NORMAL),
            RegisterInfo('dat', REG_TYPE_NORMAL),
            RegisterInfo('p0', REG_TYPE_SIMPLE),
            RegisterInfo('p1', REG_TYPE_SIMPLE),
            RegisterInfo('x0', REG_TYPE_XBUS),
            RegisterInfo('x1', REG_TYPE_XBUS),
            RegisterInfo('x2', REG_TYPE_XBUS),
            RegisterInfo('x3', REG_TYPE_XBUS),
        ],
        memory=14
    ),
}


# this is done just to make sure this logic doesn't pollute global variable namespace blah blah
def make_chip_tables_use_keys():
    global CHIPS

    for chip_name in CHIPS.keys():
        chip = CHIPS[chip_name]
        CHIPS[chip_name] = chip._replace(
            registers=OrderedDict([
                (info.name, info)
                for info in chip.registers
            ]),
        )
make_chip_tables_use_keys()


def main():
    args = get_args()

    if args.verbose:
        global verbose
        verbose = verbose_on

    root_path = os.path.abspath(args.input.name)

    try:
        chip = CHIPS.get(args.chip, None)
        verbose("selected chip {}:".format(args.chip))
        verbose("  registers:")
        for reg in chip.registers:
            verbose("    {} ({})".format(
                reg, chip.registers[reg].type
            ))
        # this dictionary will track what files we include to prevent include cycles
        # the key is the absolute path to an included file
        # the value tracks where it was included
        # for the top level file this makes no sense, so we hard code a default
        included_files = {
            os.path.abspath(root_path): SourcePosition("<root file passed to assembler>", None)
        }
        lines = read_lines(args.input, root_path, included_files)
        assembled = assemble(lines, chip)
        write_out(assembled, args.output)
    except AssemblerException as ex:
        print("error ", ex)


def write_out(instructions, path):
    """
    takes a collection of instructions and writes them out to a file
    as specified by the path argument
    """

    # TODO: compress label names to be single lettes etc?

    output = open(path, 'w')
    for inst in instructions:
        tokens = [
            piece
            for piece in [inst.label, inst.condition, inst.mneumonic] + (inst.args if inst.args is not None else [])
            if piece is not None
        ]
        spacing = ""
        if inst.label is None and inst.condition is None:
            spacing = "  "
        line = "{}{}\n".format(
            spacing,
            " ".join(tokens)
        )
        output.write(line)


def verbose_on(*args, **kwargs):
    """
    dumb wrapper for print, see verbose_off and verbose
    """
    print(*args, **kwargs)


def verbose_off(*args, **kwargs):
    """
    dummy function provides alternative to verbose_off
    """
    _ = args, kwargs


# dumb way of doing optional verbose output, see verbose_on and verbose_off
verbose = verbose_off


def assemble(lines: [LineOfSource], chip: ChipInfo) -> [Instruction]:
    """
    takes lines of text from a source file, parses them as instructions and
    produces a list of output instructions in the format SHENZHEN I/O expects
    :param lines: a list of lines for parsing as instructions
    :param chip: information about the target microchip, for providing relevant warnings
    :return: a list of instructions ready for serialising and presenting to SHENZHEN I/O
    """

    # parse inputs
    instructions = parse_lines(lines)

    # extract aliases/constants out into a dictionary
    symbol_table = symbol_pass(instructions, chip)

    # this will track the resulting instruction list
    output = []

    # this will track labels that appear on their own in a line, we'll
    # delay emitting these until we see the next instruction, then we
    # will try and put this label on the same line as the next instruction
    # this is to address situations like:
    #
    #     some_label:
    #       some code here
    #
    # where this could be on one line (SHENZHEN I/O requires you to minimise lines of code!)
    # so we try to output:
    #
    #     some_label: some code here
    lonely_labels = []

    # assemble each instruction
    for inst in instructions:
        # detect labels with no instruction, emit these as late as possible (see lonely_labels above)
        if inst.label is not None and inst.mneumonic is None:
            lonely_labels.append(inst)
            continue

        # currently all virtual instructions are handled in the symbol_pass, so ignore them
        if inst.mneumonic in VIRTUAL_INSTRUCTIONS.keys():
            continue

        # fetch instruction details and abort if unable to find some
        info = INSTRUCTIONS.get(inst.mneumonic, None)
        if info is None:
            raise AssemblerException(
                inst.source_pos,
                "unknown instruction mneumonic: {}".format(
                    inst.mneumonic
                )
            )

        # validate the arguments
        for given_arg, expected_type in zip_longest(inst.args, info.argtypes):
            # ensure the right number of arguments are provided
            if given_arg is None:
                raise AssemblerException(
                    inst.source_pos,
                    "too few arguments to {} instruction".format(
                        inst.mneumonic
                    )
                )
            if expected_type is None:
                raise AssemblerException(
                    inst.source_pos,
                    "too many arguments to {} instruction".format(
                        inst.mneumonic
                    )
                )
            # TODO: check argument types

        # perform any transformations on this instruction required
        assembled = assemble_instruction(symbol_table, chip, inst, info)

        # before we add the assembled instruction, deal with any lonely labels we've acquired!
        if len(lonely_labels) > 0:
            # if we have seen lots of labels we just have to emit them on separate lines,
            # these will be put in umcompressable_labels - this shouldn't happen often because
            # multiple labels to the same place are almost entirely pointless
            uncompressable_labels = []

            # if the instruction we're assembling already has a label we can't do anything,
            # so all lonely_labels are uncompressable
            if assembled.label is not None:
                uncompressable_labels = lonely_labels
            # the instruction has no label, so lets rebuild it with a new label!
            else:
                # only one label can win, though, the rest are uncompressable
                uncompressable_labels = lonely_labels[:-1]
                # compress only the most recent label
                to_compress = lonely_labels[-1]
                assembled = assembled.replace(
                    label=to_compress.label,
                )
            # output labels for those we can't compress and empty our lonely label list
            for label in uncompressable_labels:
                output.append(label)
            lonely_labels = []

        # finally record the assembled/translated instruction
        output.append(assembled)

    # TODO: detect unused code?
    # TODO: detect unused aliases/constants?
    # TODO: optimisation pass?

    # now we know how many lines of assembly we're generating, will it fit on the chip?
    if len(output) > chip.memory:
        print("warning: program size exceeds chip memory ({} > {})".format(
            len(output), chip.memory
        ))

    return output


def assemble_instruction(symbols: typing.Dict[str, Symbol], chip: ChipInfo, inst: [Instruction], inst_info: InstructionInfo):
    """
    assemble a single instruction
    :param symbols: the symbol table from the symbol_pass
    :param chip: information about the chip we're targetting
    :param inst: the instruction to assemble
    :param inst_info: information about the instruction mneumonic we are assembling
    :return: the instruction after any transformations have been applied
    """
    args = []

    # TODO: accumulate labels in here, then merge repeated labels?

    # replace all symbols with their value
    for given_arg, expected_Type in zip_longest(inst.args, inst_info.argtypes):
        # TODO: check references to registers are valid on current chip
        if given_arg in symbols:
            args.append(symbols[given_arg].value)
        else:
            args.append(given_arg)

    # return a transformed instruction, where the only thing that can really change is the arguments
    result = inst.replace(
        args=args,
    )
    return result


def symbol_pass(instructions: [Instruction], chip: ChipInfo):
    """
    scan through the instructions looking for aliases and constant definitions, producing a table of them
    :param instructions: the instructions to scan
    :param chip: information about the target chip, in order to diagnose bad register aliases
    :return: a dictionary of symbols
    """
    result = {}

    # scan each instruction
    for inst in instructions:
        # if it isn't an alias/const then we don't care, skip it
        if inst.mneumonic not in (FAKE_OP_ALIAS, FAKE_OP_CONST):
            continue

        # check we have enough arguments
        if len(inst.args) < 2:
            raise AssemblerException(
                inst.source_pos,
                "expected two arguments to {}: name and value".format(
                    inst.mneumonic
                )
            )

        name = inst.args[0]
        value = inst.args[1]

        if name in result:
            raise AssemblerException(
                inst.source_pos,
                "redefinition of symbol '{}', previously declared here: {}".format(
                    name, result[name].source_pos
                )
            )

        # ensure that the name of the alias/const isn't going to collide with any register names!
        if chip.registers.get(name, None):
            raise AssemblerException(
                inst.source_pos,
                "cannot use {} as an {} name, reserved as a register name on this chip".format(
                    name, inst.mneumonic
                )
            )

        # ensure that any aliases actually refer to real registers!
        if inst.mneumonic == FAKE_OP_ALIAS and chip.registers.get(value, None) is None:
            raise AssemblerException(
                inst.source_pos,
                "{} is an invalid alias as '{}' is not a valid register name on this chip".format(
                    name, value
                )
            )

        # ensure that constants are valid
        if inst.mneumonic == FAKE_OP_CONST:
            # we currently only support integer literal constants

            # ensure it parses as an integer
            try:
                as_integer = int(value)
            except:
                raise AssemblerException(
                    inst.source_pos,
                    "constants currently only support integer literals"
                )

            # ensure it's within the range of integers that SHENZHEN I/O requires
            if not (-999 <= as_integer <= 999):
                raise AssemblerException(
                    inst.source_pos,
                    "integer constants must be between -999 and 999 inclusive"
                )

        # record the new alias/const
        verbose("symbol {} is {} of {}".format(
            name, inst.mneumonic, value
        ))
        result[name] = Symbol(
            source_pos=inst.source_pos,
            name=name,
            value=value
        )
    return result


def parse_lines(lines: [LineOfSource]) -> [Instruction]:
    """
    takes a collection of lines and parses them into instructions
    :param lines: the lines to parse
    :return: the resulting instruction list
    """
    return list(
        filter(
            lambda x: x is not None,
            map(
                parse_line,
                lines
            )
        )
    )


def parse_line(line: LineOfSource) -> Instruction:
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
        raise AssemblerException(
            line.pos,
            "condition symbol '{}' found with no associated instruction?".format(
                condition
            )
        )
    return Instruction(line.pos, label, condition, mneumonic, args)


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
            included_path = os.path.abspath(included_path[1:-1])

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


def get_args() -> argparse.Namespace:
    """
    utility method that handles the argument parsing via argparse
    :return: the result of using argparse to parse the command line arguments
    """
    parser = argparse.ArgumentParser(
        description="simple assembler/compiler for making it easier to write SHENZHEN.IO programs"
    )
    parser.add_argument(
        'input', type=argparse.FileType(),
        help="the input file to ingest"
    )
    parser.add_argument(
        '-o', '--output',
        help='the output file path', default='out.asm'
    )
    parser.add_argument(
        '-c', '--chip', choices=CHIPS.keys(), default=CHIP_TYPE_MC6000,
        help='inform assembler of target chip for better diagnostics'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='flag to cause more verbose output during execution'
    )
    return parser.parse_args()


# TODO: don't use exceptions for errors, accumulate them and only stop when forced?
class AssemblerException(Exception):
    """custom exception class so that we only catch our own, not internal fatal ones"""

    def __init__(self, source_pos, message):
        """
        constructor
        :param source_pos: the source position of the error
        :param message: a description of the failure
        """
        super().__init__("[{}]: {}".format(source_pos, message))


if __name__ == "__main__":
    main()
