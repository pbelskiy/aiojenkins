import inspect
import os
import platform
import time

from aiojenkins import Jenkins
from aiojenkins.utils import construct_job_config


class CreateJob:
    # cannot use contextlib.asynccontextmanager now due Python 3.6 support
    def __init__(self, *args, **kwargs):
        function_name = inspect.stack()[1].function
        self.name = '{}_{}'.format(function_name, time.time())
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        job_config = construct_job_config(*self.args, **self.kwargs)
        await jenkins.jobs.create(self.name, job_config)
        return self.name

    async def __aexit__(self, exc_type, exc, tb):
        await jenkins.jobs.delete(self.name)


def get_host():
    return os.environ.get('host', 'http://localhost:8080')


def get_login():
    return os.environ.get('login', 'admin')


def get_password():
    return os.environ.get('password', 'admin')


def is_locally():
    """
    For skipping some long tests locally, but not on completely CI
    """
    return (platform.system() == 'Darwin')


jenkins = Jenkins(get_host(), get_login(), get_password())
