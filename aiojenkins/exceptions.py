from typing import Optional


class JenkinsError(Exception):
    def __init__(self, message: Optional[str] = None, status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status = status


class JenkinsNotFoundError(JenkinsError):
    ...
