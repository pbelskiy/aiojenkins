#!/usr/bin/python3

import pytest

from tests import jenkins, HOST_ADDR

from aiojenkins import Jenkins
from aiojenkins.exceptions import JenkinsError


@pytest.mark.asyncio
async def test_authentication_error():
    jenkins = Jenkins(HOST_ADDR, 'random-login', 'random-password')

    with pytest.raises(JenkinsError):
        version = await jenkins.get_version()
        # was introduced  default admin with password
        if version.major >= 2:
            await jenkins.nodes.disable('master')
        else:
            raise JenkinsError


@pytest.mark.asyncio
async def test_get_status():
    await jenkins.get_status()
