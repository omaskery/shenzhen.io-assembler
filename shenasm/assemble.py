from collections import namedtuple
from itertools import zip_longest
import typing


from .instructions import INSTRUCTIONS, VIRTUAL_INSTRUCTIONS, InstructionInfo, FAKE_OP_CONST, FAKE_OP_ALIAS
from .parse import Instruction, parse_lines
from .errors import AssemblerException
from .source import LineOfSource
from .chips import ChipInfo
from . import log


Symbol = namedtuple('Symbol', 'source_pos name value')


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


def symbol_pass(instructions: [Instruction], chip: ChipInfo) -> typing.Dict[str, Symbol]:
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
        log.verbose("symbol {} is {} of {}".format(
            name, inst.mneumonic, value
        ))
        result[name] = Symbol(
            source_pos=inst.source_pos,
            name=name,
            value=value
        )
    return result
