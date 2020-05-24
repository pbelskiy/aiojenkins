import os
import platform

from aiojenkins import Jenkins


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
