

class InstructionInfo(object):

    def __init__(self, mnemonic, argtypes):
        self._mnemonic = mnemonic
        self._argtypes = argtypes

    @property
    def mnemonic(self):
        return self._mnemonic

    @property
    def argtypes(self):
        return self._argtypes


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
        mnemonic=CHIP_OP_NOP,
        argtypes=[],
    ),
    CHIP_OP_MOV: InstructionInfo(
        mnemonic=CHIP_OP_MOV,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG],
        ],
    ),
    CHIP_OP_JMP: InstructionInfo(
        mnemonic=CHIP_OP_JMP,
        argtypes=[
            [INST_ARG_TYPE_LBL],
        ],
    ),
    CHIP_OP_SLP: InstructionInfo(
        mnemonic=CHIP_OP_SLP,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_SLX: InstructionInfo(
        mnemonic=CHIP_OP_SLX,
        argtypes=[
            [INST_ARG_TYPE_XBUS_PIN],
        ],
    ),
    CHIP_OP_ADD: InstructionInfo(
        mnemonic=CHIP_OP_ADD,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_SUB: InstructionInfo(
        mnemonic=CHIP_OP_SUB,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_MUL: InstructionInfo(
        mnemonic=CHIP_OP_MUL,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_NOT: InstructionInfo(
        mnemonic=CHIP_OP_NOT,
        argtypes=[],
    ),
    CHIP_OP_DGT: InstructionInfo(
        mnemonic=CHIP_OP_DGT,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_DST: InstructionInfo(
        mnemonic=CHIP_OP_DST,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TEQ: InstructionInfo(
        mnemonic=CHIP_OP_TEQ,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TGT: InstructionInfo(
        mnemonic=CHIP_OP_TGT,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TLT: InstructionInfo(
        mnemonic=CHIP_OP_TLT,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_TCP: InstructionInfo(
        mnemonic=CHIP_OP_TCP,
        argtypes=[
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
    CHIP_OP_GEN: InstructionInfo(
        mnemonic=CHIP_OP_GEN,
        argtypes=[
            [INST_ARG_TYPE_PIN],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
            [INST_ARG_TYPE_REG, INST_ARG_TYPE_INT],
        ],
    ),
}

VIRTUAL_INSTRUCTIONS = {
    FAKE_OP_ALIAS: InstructionInfo(
        mnemonic=FAKE_OP_ALIAS,
        argtypes=[
            [INST_ARG_TYPE_NAME],
            [INST_ARG_TYPE_REG],
        ]
    ),
    FAKE_OP_CONST: InstructionInfo(
        mnemonic=FAKE_OP_CONST,
        argtypes=[
            [INST_ARG_TYPE_NAME],
            [INST_ARG_TYPE_INT],
        ]
    ),
}
