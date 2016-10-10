

# TODO: don't use exceptions for errors, accumulate them and only stop when forced?
class AssemblerException(Exception):
    """custom exception class so that we only catch our own, not internal fatal ones"""

    def __init__(self, source_pos, message):
        """
        constructor
        :param source_pos: the source position of the error
        :param message: a description of the failure
        """
        super().__init__("[{}]: {}".format(source_pos, message))
