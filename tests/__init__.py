import os

from aiojenkins import Jenkins

HOST_ADDR = os.environ.get('host', 'http://localhost:8080')

jenkins = Jenkins(
    HOST_ADDR,
    os.environ.get('login', 'admin'),
    os.environ.get('password', 'admin')
)
