"""Exceptions raise by Apps."""


class ParslError(Exception):
    """Base class for all exceptions.

    Only to be invoked when a more specific error is not available.
    """


class NotFutureError(ParslError):
    """A non future item was passed to a function that expected a future.

    This is basically a type error.
    """


class InvalidAppTypeError(ParslError):
    """An invalid app type was requested from the @App decorator."""


class AppException(ParslError):
    """An error raised during execution of an app.

    What this exception contains depends entirely on context
    """

    def __repr__(self):
        return "{0} Reason:{1}".format(self.__class__, self.reason)

    def __str__(self):
        return self.__repr__()


class AppBadFormatting(ParslError):
    """An error raised during formatting of a bash function.

    What this exception contains depends entirely on context
    Contains:
    reason(string)
    exitcode(int)
    retries(int/None)
    """

    def __init__(self, reason, exitcode, retries=None):
        super().__init__()
        self.reason = reason
        self.exitcode = exitcode
        self.retries = retries


class AppFailure(AppException):
    """An error raised during execution of an app.

    What this exception contains depends entirely on context
    Contains:
    reason(string)
    exitcode(int)
    retries(int/None)
    """

    def __init__(self, reason, exitcode, retries=None):
        super().__init__()
        self.reason = reason
        self.exitcode = exitcode
        self.retries = retries


class AppTimeout(AppException):
    """An error raised during execution of an app when it exceeds its allotted walltime.

    Contains:
    reason(string)
    exitcode(int)
    retries(int/None)
    """

    def __init__(self, reason, exitcode, retries=None):
        super().__init__()
        self.reason = reason
        self.exitcode = -55
        self.retries = retries


class BashAppNoReturn(AppException):
    """Bash app returned no string.

    Contains:
    reason(string)
    exitcode(int)
    retries(int/None)
    """

    def __init__(self, reason, exitcode, retries=None):
        super().__init__()
        self.reason = reason
        self.exitcode = -21
        self.retries = retries


class MissingOutputs(ParslError):
    """Error raised at the end of app execution due to missing output files.

    Contains:
    reason(string)
    outputs(List of strings/files..)
    """

    def __init__(self, reason, outputs):
        super().__init__()
        self.reason = reason
        self.outputs = outputs

    def __repr__(self):
        return "Missing Outputs: {0}, Reason:{1}".format(self.outputs, self.reason)

    def __str__(self):
        return "Reason:{0} Missing:{1}".format(self.reason, self.outputs)


class BadStdStreamFile(ParslError):
    """Error raised due to bad filepaths specified for STDOUT/ STDERR.

    Contains:
       reason(string)
       outputs(List of strings/files..)
       exception object
    """

    def __init__(self, outputs, exception):
        super().__init__()
        self._outputs = outputs
        self._exception = exception

    def __repr__(self):
        return "FilePath:[{}] Exception:{}".format(self._outputs,
                                                   self._exception)

    def __str__(self):
        return self.__repr__()


class DependencyError(ParslError):
    """Error raised at the end of app execution due to missing output files.

    Contains:
    reason(string)
    outputs(List of strings/files..)
    """

    def __init__(self, dependent_exceptions, reason, outputs):
        super().__init__()
        self.dependent_exceptions = dependent_exceptions
        self.reason = reason
        self.outputs = outputs

    def __repr__(self):
        return "Missing Outputs: {0}, Reason:{1}".format(self.outputs, self.reason)

    def __str__(self):
        return "Reason:{0} Missing:{1}".format(self.reason, self.outputs)
