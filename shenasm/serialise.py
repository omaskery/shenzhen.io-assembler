

def write_out(instructions, path):
    """
    takes a collection of instructions and writes them out to a file
    as specified by the path argument
    """

    # TODO: compress label names to be single letters etc?

    output = open(path, 'w')
    for inst in instructions:
        tokens = [
            piece
            for piece in [inst.label, inst.condition, inst.mnemonic] + (inst.args if inst.args is not None else [])
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
