from .exceptions import JenkinsError, JenkinsNotFoundError
from .jenkins import Jenkins

__version__ = '0.6.2'

__all__ = ('Jenkins', 'JenkinsError', 'JenkinsNotFoundError')
