#!/usr/bin/python3

import pytest

from tests import jenkins, HOST_ADDR

from aiojenkins import Jenkins
from aiojenkins.exceptions import JenkinsError


@pytest.mark.asyncio
async def test_authentication_error():
    jenkins = Jenkins(HOST_ADDR, 'random-login', 'random-password')
    with pytest.raises(JenkinsError):
        await jenkins.nodes.disable('master')


@pytest.mark.asyncio
async def test_get_status():
    await jenkins.get_status()
