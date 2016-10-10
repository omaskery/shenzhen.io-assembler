from collections import namedtuple


WARNING = 'warning'
ERROR = 'error'


class Issue(namedtuple('Issue', 'level source_pos message')):
    """records information about an issue that was encountered during assembler execution"""

    def __str__(self):
        return "{} line {}: {} - {}".format(
            self.source_pos.file,
            self.source_pos.line,
            self.level,
            self.message
        )


class IssueLog(object):
    """collects all issues that occur during assembler execution"""

    def __init__(self):
        self._log = []

    @property
    def issues(self): return self._log

    @property
    def warnings(self): return list(filter(lambda issue: issue.level == WARNING, self.issues))

    @property
    def errors(self): return list(filter(lambda issue: issue.level == ERROR, self.issues))

    def warning(self, source_pos, message, *args):
        """
        emits a warning to the issue log
        :param source_pos: the position in the source that the warning refers to
        :param message: a description of the issue
        :param args: arguments to be forwarded to message.format(*args)
        """
        self._log.append(
            Issue(WARNING, source_pos, message.format(*args))
        )

    def error(self, source_pos, message, *args):
        """
        emits an error to the issue log
        :param source_pos: the position in the source that the error refers to
        :param message: a description of the issue
        :param args: arguments to be forwarded to message.format(*args)
        """
        self._log.append(
            Issue(ERROR, source_pos, message.format(*args))
        )
