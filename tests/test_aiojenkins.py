#!/usr/bin/python3

import pytest

from tests import jenkins, HOST_ADDR

from aiojenkins import Jenkins
from aiojenkins.exceptions import JenkinsError, JenkinsNotFoundError


@pytest.mark.asyncio
async def test_authentication_error():
    with pytest.raises(JenkinsError):
        await Jenkins(HOST_ADDR, 'random-login', 'random-password').get_status()


@pytest.mark.asyncio
async def test_get_status():
    await jenkins.get_status()
