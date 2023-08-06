class RetryException(Exception):
    """
    Special exception that does not log an exception when it is received.
    This is a retryable error.
    """
    def __init__(self, *args, **kwargs):
        super(RetryException, self).__init__(*args, **kwargs)
        if 'exc' in kwargs:
            self.exc = kwargs['exc']


class ValidationError(Exception):
    """
    Message failed JSON schema validation
    """
    pass


class ConfigurationError(Exception):
    """
    There was some problem with settings
    """
    pass


class TaskNotFound(Exception):
    """
    No task was found that can handle the given message. Ensure that you call `taskhawk.RegisterTask`.
    """
    pass
