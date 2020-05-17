class JenkinsError(Exception):
    def __init__(self, message=None, status=None):
        self.message = message
        self.status = status


class JenkinsNotFoundError(JenkinsError):
    ...
