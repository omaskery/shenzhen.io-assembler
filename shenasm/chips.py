from collections import OrderedDict
from collections import namedtuple


class ChipInfo(namedtuple('ChipInfo', 'registers memory')):

    def replace(self, **kwargs):
        return self._replace(**kwargs)


RegisterInfo = namedtuple('RegisterInfo', 'name type')


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
