from . import log
import string


def write_out(instructions, path):
    """
    takes a collection of instructions and writes them out to a file
    as specified by the path argument
    """

    compressed_labels = {}
    labels = label_generator()

    output = open(path, 'w')
    for inst in instructions:
        label = None
        if inst.label is not None:
            label = compressed_labels.get(inst.label, None)
            if label is None:
                label = next(labels) + ":"
                compressed_labels[inst.label] = label
                log.verbose("compressing label {} to {}".format(inst.label, label))

        tokens = [
            piece
            for piece in [label, inst.condition, inst.mnemonic] + (inst.args if inst.args is not None else [])
            if piece is not None
        ]
        spacing = ""
        if label is None and inst.condition is None:
            spacing = "  "
        line = "{}{}\n".format(
            spacing,
            " ".join(tokens)
        )
        output.write(line)


def label_generator():
    """
    generates labels for label compression, in the form:
      a, b, c, ..., x, y, z, aa, ab, ac, ... , ay, az, ba, ...
    """
    for l in string.ascii_letters:
        yield l

    for prefix in label_generator():
        for l in string.ascii_letters:
            yield prefix + l
