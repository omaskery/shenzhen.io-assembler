#!/usr/bin/env python3

import argparse
import typing
import sys
import io
import os


import shenasm


def main():
    args = get_args()
    result = 0

    if args.verbose:
        shenasm.log.verbose = shenasm.log.verbose_on

    root_path = os.path.abspath(args.input.name)

    issues = shenasm.errors.IssueLog()

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
        str(os.path.abspath(root_path)): shenasm.source.SourcePosition("<root file passed to assembler>", None)
    }
    lines = shenasm.source.read_lines(issues, args.input, root_path, included_files)

    assembled, ir_nodes = shenasm.assemble.assemble(issues, lines, chip)
    if args.dotfile is not None:
        shenasm.intermediate.output_ir_dotfile(args.dotfile, ir_nodes)
        print("wrote intermediate representation graph to dotfile: {}".format(args.dotfile))

    if len(issues.issues) > 0:
        print("{} warnings and {} errors".format(
            len(issues.warnings),
            len(issues.errors)
        ))
        for issue in issues.issues:
            print(issue)

    if len(issues.errors) < 1:
        shenasm.serialise.write_out(assembled, args.output)
    else:
        print("output inhibited due to errors")
        result = -1

    sys.exit(result)


class ProgramArgs(argparse.Namespace):

    def __init__(self):
        super().__init__()
        self.verbose = False
        self.input = typing.cast(io.FileIO, None)
        self.chip = ""
        self.output = typing.cast(io.FileIO, None)
        self.dotfile = ""


def get_args() -> ProgramArgs:
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
    parser.add_argument(
        '--dotfile', type=str, default=None,
        help='write a graphviz compatible .dot file containing the intermediate representation graph of the input'
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
