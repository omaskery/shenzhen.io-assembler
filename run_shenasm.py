import argparse
import os


import shenasm


def main():
    args = get_args()

    if args.verbose:
        shenasm.log.verbose = shenasm.log.verbose_on

    root_path = os.path.abspath(args.input.name)

    try:
        chip = shenasm.chips.lookup_by_name(args.chip)
        shenasm.log.verbose("selected chip {}:".format(args.chip))
        shenasm.log.verbose("  registers:")
        for reg in chip.registers:
            shenasm.log.verbose("    {} ({})".format(
                reg, chip.registers[reg].type
            ))
        # this dictionary will track what files we include to prevent include cycles
        # the key is the absolute path to an included file
        # the value tracks where it was included
        # for the top level file this makes no sense, so we hard code a default
        included_files = {
            os.path.abspath(root_path): shenasm.source.SourcePosition("<root file passed to assembler>", None)
        }
        lines = shenasm.source.read_lines(args.input, root_path, included_files)
        assembled = shenasm.assemble.assemble(lines, chip)
        shenasm.serialise.write_out(assembled, args.output)
    except shenasm.errors.AssemblerException as ex:
        print("error ", ex)


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
        '-c', '--chip', choices=shenasm.chips.list_names(), default=shenasm.chips.CHIP_TYPE_MC6000,
        help='inform assembler of target chip for better diagnostics'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='flag to cause more verbose output during execution'
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
