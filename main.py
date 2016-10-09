from collections import OrderedDict
from collections import namedtuple
import argparse


ChipInfo = namedtuple('ChipInfo', 'registers memory')
RegisterInfo = namedtuple('RegisterInfo', 'name type')
Symbol = namedtuple('Symbol', 'lineno name value')
InstructionInfo = namedtuple('InstructionInfo', 'mneumonic argtypes')
Instruction = namedtuple('Instruction', 'lineno label condition mneumonic args')


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


for chip_name in CHIPS.keys():
    chip = CHIPS[chip_name]
    CHIPS[chip_name] = ChipInfo(
        registers=OrderedDict([
            (info.name, info)
            for info in chip.registers
        ]),
        memory=chip.memory
    )


def main():
    args = get_args()

    try:
        chip = CHIPS.get(args.chip, None)
        print("selected chip {}:".format(args.chip))
        print("  registers:")
        for reg in chip.registers:
            print("    {} ({})".format(
                reg, chip.registers[reg].type
            ))
        lines = read_lines(args.input)
        assembled = assemble(lines, chip)
        write_out(assembled, args.output)
    except AssemblerException as ex:
        print("error:", ex)


def write_out(instructions, path):
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


def assemble(lines, chip):
    instructions = parse_lines(lines)
    symbol_table = symbol_pass(instructions, chip)
    output = []

    lonely_labels = []

    for inst in instructions:
        if inst.label is not None and inst.mneumonic is None:
            lonely_labels.append(inst)
            continue

        if inst.mneumonic in VIRTUAL_INSTRUCTIONS.keys():
            continue

        info = INSTRUCTIONS.get(inst.mneumonic, None)
        if info is None:
            raise AssemblerException(
                inst.lineno,
                "unknown instruction mneumonic: {}".format(
                    inst.mneumonic
                )
            )

        for given_arg, expected_type in zip(inst.args, info.argtypes):
            if given_arg is None:
                raise AssemblerException(
                    inst.lineno,
                    "too few arguments to {} instruction".format(
                        inst.mneumonic
                    )
                )
            if expected_type is None:
                raise AssemblerException(
                    inst.lineno,
                    "too many arguments to {} instruction".format(
                        inst.mneumonic
                    )
                )

        assembled = assemble_instruction(symbol_table, chip, inst, info)
        if len(lonely_labels) > 0:
            if assembled.label is not None:
                for label in lonely_labels:
                    output.append(label)
            else:
                extra = lonely_labels[:-1]
                compressed = lonely_labels[-1]
                assembled = Instruction(
                    lineno=assembled.lineno,
                    label=compressed.label,
                    condition=assembled.condition,
                    mneumonic=assembled.mneumonic,
                    args=assembled.args
                )
                for label in extra:
                    output.append(label)
            lonely_labels = []
        output.append(assembled)
    return output


def assemble_instruction(symbols, chip, inst, inst_info):
    args = []

    for given_arg, expected_Type in zip(inst.args, inst_info.argtypes):
        if given_arg in symbols:
            args.append(symbols[given_arg].value)
        else:
            args.append(given_arg)

    return Instruction(
        lineno=inst.lineno,
        label=inst.label,
        condition=inst.condition,
        mneumonic=inst.mneumonic,
        args=args,
    )


def symbol_pass(instructions, chip):
    result = {}
    for inst in instructions:
        if inst.mneumonic in (FAKE_OP_ALIAS, FAKE_OP_CONST):
            if len(inst.args) < 2:
                raise AssemblerException(
                    inst.lineno,
                    "expected two arguments to {}: name and value".format(
                        inst.mneumonic
                    )
                )

            name = inst.args[0]
            value = inst.args[1]

            if chip.registers.get(name, None):
                raise AssemblerException(
                    inst.lineno,
                    "cannot use {} as an {} name, reserved as a register name on this chip".format(
                        name, inst.mneumonic
                    )
                )

            if inst.mneumonic == FAKE_OP_ALIAS and chip.registers.get(value, None) is None:
                raise AssemblerException(
                    inst.lineno,
                    "{} is an invalid alias as '{}' is not a valid register name on this chip".format(
                        name, value
                    )
                )

            print("symbol {} is {} of {}".format(
                name, inst.mneumonic, value
            ))
            result[name] = Symbol(inst.lineno, name, value)
    return result


def parse_lines(lines):
    return list(
        filter(
            lambda x: x is not None,
            map(
                parse_line,
                lines
            )
        )
    )


def parse_line(line):
    number, line = line
    # remove comments
    comment_start = line.find("#")
    if comment_start != -1:
        line = line[:comment_start]
    line = line.strip()

    # empty lines don't need parsing
    if not line:
        return None

    # parse by spaces
    tokens = line.split(" ")
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
            number,
            "condition symbol '{}' found with no associated instruction?".format(
                condition
            )
        )
    return Instruction(number, label, condition, mneumonic, args)


def read_lines(file):
    return [
        (number, line.strip())
        for number, line in enumerate(file.readlines(), start=1)
    ]


def get_args():
    parser = argparse.ArgumentParser(
        description="simple assembler/compiler for making it easier to write SHENZHEN.IO programs"
    )
    parser.add_argument(
        'input', type=argparse.FileType(), help="the input file to ingest"
    )
    parser.add_argument(
        '-o', '--output', help='the output file path', default='out.asm'
    )
    parser.add_argument(
        '-c', '--chip', choices=CHIPS.keys(), default=CHIP_TYPE_MC6000
    )
    return parser.parse_args()


class AssemblerException(Exception):
    def __init__(self, lineno, message):
        super().__init__("[line {}]: {}".format(lineno, message))


if __name__ == "__main__":
    main()
