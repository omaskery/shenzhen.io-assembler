from collections import namedtuple


InstructionInfo = namedtuple('InstructionInfo', 'mneumonic argtypes')


INST_ARG_TYPE_REG = 0
INST_ARG_TYPE_INT = 1
INST_ARG_TYPE_LBL = 2
INST_ARG_TYPE_PIN = 3
INST_ARG_TYPE_SIMPLE_PIN = 4
INST_ARG_TYPE_XBUS_PIN = 5
INST_ARG_TYPE_NAME = 6

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
            [INST_ARG_TYPE_PIN],
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
