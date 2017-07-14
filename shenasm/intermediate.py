import typing
import uuid


from .instructions import CHIP_OP_TEQ, CHIP_OP_TGT, CHIP_OP_TLT, CHIP_OP_TCP, CHIP_OP_JMP
from .parse import Instruction
from .errors import IssueLog
from . import log


UNCONDITIONAL = None
TRUE_CONDITIONAL = '+'
FALSE_CONDITIONAL = '-'


class IntermediateNode(object):

    def __init__(self, instructions: [Instruction] = None, incoming: ['IntermediateNode'] = None, exits: typing.Dict[str, 'IntermediateNode'] = None, creation_reason: str = None):
        self.uid = uuid.uuid4()
        self.creation_reason = creation_reason
        self.incoming = incoming if incoming is not None else []
        self.instructions = instructions if instructions is not None else []
        self.exits = exits if exits is not None else {}

    @property
    def first_instruction(self):
        return self.instructions[0]

    @property
    def last_instruction(self):
        return self.instructions[-1]

    def is_orphan(self, entry_node):
        orphaned = False

        if self is not entry_node:
            orphaned = True

            to_check = [] + self.incoming
            while len(to_check) > 0:
                ancestor = to_check.pop(0)
                if ancestor is entry_node:
                    orphaned = False
                    break
                to_check.extend(ancestor.incoming)

        return orphaned

    @staticmethod
    def create_child_of(incoming: ['IntermediateNode'], exit_key: str, instructions: [Instruction]):
        result = IntermediateNode(incoming, instructions)
        incoming.exits[exit_key] = result
        return result


def build_ir_graph(issues: IssueLog, instructions: [Instruction]):
    # first divide the program into 'regions', each region consists of
    # a group of instructions that can always execute together:
    #  - adjacent unconditional instructions (except when a label is involved)
    #  - adjacent conditional instructions with the same condition flag where the previous instruction is not a test
    #  - jump instructions always terminate a block
    regions = []
    label_to_region = {}
    for instruction in instructions:
        if len(regions) < 1:
            regions.append(IntermediateNode([instruction], creation_reason="first"))
        else:
            if is_jump_instruction(regions[-1].last_instruction):
                regions.append(IntermediateNode([instruction], creation_reason="last instruction was a jump"))
            elif instruction.condition is None and (instruction.label is not None or regions[-1].last_instruction.condition is not None):
                if instruction.label is not None:
                    regions.append(IntermediateNode([instruction], creation_reason="starts with label"))
                elif regions[-1].last_instruction.condition is not None:
                    regions.append(IntermediateNode([instruction], creation_reason="unconditional after conditional"))
            elif instruction.condition is not None:
                if is_test_instruction(regions[-1].last_instruction):
                    regions.append(IntermediateNode([instruction], creation_reason="last instruction was a test"))
                elif instruction.condition != regions[-1].last_instruction.condition:
                    regions.append(IntermediateNode([instruction], creation_reason="different conditional to last conditional"))
                else:
                    regions[-1].instructions.append(instruction)
            else:
                regions[-1].instructions.append(instruction)

    # go through and record what labels point to what nodes in our intermediate graph
    #   we should have orchestrated it so that all labels are the first instruction of a node
    for region in regions:
        first_instruction = region.first_instruction
        if first_instruction.label is not None:
            label_without_trailing_colon = first_instruction.label[:-1]
            label_to_region[label_without_trailing_colon] = region
            log.verbose("label '{}' points to region {}".format(first_instruction.label, region.uid))

    # now go through each ir node and work out what its 'children' (exits) are (where could execution go next?)
    for index in range(len(regions)):
        after = regions[index+1:]
        current = regions[index]

        # jump instructions are treated specially, they always just go where they say
        if is_jump_instruction(current.instructions[-1]):
            target_label = current.instructions[-1].args[0]
            target = label_to_region.get(target_label, None)

            if target is None:
                issues.error(current.instructions[-1].source_pos, "jump to non-existent label '{}'", target_label)
            else:
                current.exits[UNCONDITIONAL] = target
                target.incoming.append(current)
        # every other instruction will go to whatever next instruction makes sense based on
        # the current and subsequent instructions' condition flags
        else:
            first_positive_condition = None
            first_negative_condition = None
            first_unconditional = None

            # there can only be a positive branch if we aren't in a negative branch, because by definition we know
            # the test register is negative in that case, UNLESS the instruction is a test!
            can_branch_positive = current.first_instruction.condition != '-' or is_test_instruction(current.first_instruction)
            # there can only be a negative branch if we aren't in a positive branch, because by definition we know
            # the test register is positive in that case, UNLESS the instruction is a test!
            can_branch_negative = current.first_instruction.condition != '+' or is_test_instruction(current.first_instruction)

            # find the first positive and negative conditional instructions, but stop looking if you find
            # an unconditional instruction first.
            for inner_region in after:
                # only look for positive conditional instructions if we can branch positively and haven't found one yet
                if can_branch_positive and first_positive_condition is None and inner_region.first_instruction.condition == '+':
                    first_positive_condition = inner_region
                # only look for negative conditional instructions if we can branch negatively and haven't found one yet
                elif can_branch_negative and first_negative_condition is None and inner_region.first_instruction.condition == '-':
                    first_negative_condition = inner_region
                # if we find an unconditional instruction stop
                elif inner_region.first_instruction.condition is None:
                    first_unconditional = inner_region
                    break

                # if we've found both a positive and negative conditional instruction then we can stop
                if None not in (first_positive_condition, first_negative_condition):
                    break

            # identify what regions we can branch to based on our search
            true_target, false_target = None, None
            if can_branch_positive:
                true_target = first_positive_condition if first_positive_condition is not None else first_unconditional
            if can_branch_negative:
                false_target = first_negative_condition if first_negative_condition is not None else first_unconditional

            # if our true and false targets are the same, it's by definition unconditional!
            if true_target is false_target and true_target is not None:
                current.exits[UNCONDITIONAL] = true_target
                true_target.incoming.append(current)
            # we might have conditional branches, so try and connect up the true and false branches to their targets
            else:
                if true_target is not None:
                    # if there isn't a false target, then this is actually unconditional
                    condition = TRUE_CONDITIONAL if false_target is not None else UNCONDITIONAL
                    current.exits[condition] = true_target
                    true_target.incoming.append(current)
                if false_target is not None:
                    # if there isn't a true target, then this is actually unconditional
                    condition = FALSE_CONDITIONAL if true_target is not None else UNCONDITIONAL
                    current.exits[condition] = false_target
                    false_target.incoming.append(current)

    return regions


def output_ir_dotfile(path, ir_nodes):
    dotfile = open(path, 'w')

    def dot(x, *args):
        dotfile.write(x.format(*args) + "\n")

    def node2name(node):
        return "node{}".format(
            str(node.uid).replace("-", "")
        )

    black = "black"
    unconditional_colour = "#bae1ff"
    true_colour = "#baffc9"
    false_colour = "#ffb3ba"
    jump_colour = "#ffdfba"
    orphan_colour = "#eeeeee"

    dot("digraph prof {{")
    dot("  ratio = fill;")
    dot("  node [style=filled];")
    dot("")
    dot("  ENTRY -> {};", node2name(ir_nodes[0]))
    for region in ir_nodes:
        for transition_type, target in region.exits.items():
            colour = black
            label = ""
            if transition_type is not None:
                if transition_type == "+":
                    colour = true_colour
                    label = "true"
                else:
                    colour = false_colour
                    label = "false"
            elif is_jump_instruction(region.instructions[-1]):
                colour = jump_colour
            if region.is_orphan(ir_nodes[0]):
                colour = orphan_colour
            dot("  {} -> {} [label=\"{}\" color=\"{}\"];".format(
                node2name(region),
                node2name(target),
                label,
                colour
            ))

    dot("")

    dot("  ENTRY;")
    for region in ir_nodes:
        colour = unconditional_colour
        if region.is_orphan(ir_nodes[0]):
            colour = orphan_colour
        elif is_jump_instruction(region.instructions[-1]):
            colour = jump_colour
        elif region.instructions[0].condition is not None:
            if region.instructions[0].condition == "+":
                colour = true_colour
            else:
                colour = false_colour
        dot("  {} [label=\"{}\" color=\"{}\" shape=rectangle labeljust=l];".format(
            node2name(region),
            "\\l".join(map(str, region.instructions)) + "\\l",
            colour
        ))
    dot("}}")


def warn_unused_code(issues, ir_nodes):
    entry_node = ir_nodes[0]
    for node in ir_nodes[1:]:
        if node.is_orphan(entry_node):
            issues.warning(
                node.instructions[0].source_pos,
                "unreachable instructions between lines {} and {}?",
                node.instructions[0].source_pos.line,
                node.instructions[-1].source_pos.line
            )


def node_contains_test(node: IntermediateNode):
    return any(map(is_test_instruction, node.instructions))


def is_test_instruction(instruction):
    return instruction.mnemonic in (CHIP_OP_TEQ, CHIP_OP_TGT, CHIP_OP_TLT, CHIP_OP_TCP)


def is_jump_instruction(instruction):
    return instruction.mnemonic in (CHIP_OP_JMP,)


def opposite_branch_sign_of(sign):
    return {
        TRUE_CONDITIONAL: FALSE_CONDITIONAL,
        FALSE_CONDITIONAL: TRUE_CONDITIONAL,
    }[sign]
