from collections import OrderedDict


class ChipInfo(object):

    def __init__(self, registers, memory):
        self._registers = registers
        self._memory = memory

    @property
    def registers(self):
        return self._registers

    @property
    def memory(self):
        return self._memory

    def replace(self, **kwargs):
        return ChipInfo(
            kwargs.get("registers", self.registers),
            kwargs.get("memory", self.memory)
        )


class RegisterInfo(object):

    def __init__(self, name, reg_type):
        self._name = name
        self._type = reg_type

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type


REG_TYPE_NORMAL = 'normal'
REG_TYPE_SIMPLE = 'simple'
REG_TYPE_XBUS = 'xbus'


CHIP_TYPE_MC4000 = 'MC4000'
CHIP_TYPE_MC4000X = 'MC4000X'
CHIP_TYPE_MC6000 = 'MC6000'


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
        CHIPS[chip_name] = chip.replace(
            registers=OrderedDict([
                (info.name, info)
                for info in chip.registers
            ]),
        )
make_chip_tables_use_keys()


def lookup_by_name(name):
    return CHIPS.get(name, None)


def list_names():
    return CHIPS.keys()
