#!/usr/bin/python3

import contextlib
import pytest

from tests import (
    jenkins,
    JENKINS_HOST,
    JENKINS_LOGIN,
    JOB_CONFIG_XML,
)

from aiojenkins import Jenkins
from aiojenkins.exceptions import JenkinsError, JenkinsNotFoundError


@pytest.mark.asyncio
async def test_authentication_error():
    jenkins = Jenkins(JENKINS_HOST, 'random-login', 'random-password')

    with pytest.raises(JenkinsError):
        version = await jenkins.get_version()
        # was introduced  default admin with password
        if version.major >= 2:
            await jenkins.nodes.disable('master')
        else:
            raise JenkinsError


@pytest.mark.asyncio
async def test_invalid_host():
    with pytest.raises(JenkinsError):
        jenkins = Jenkins('@#$')
        await jenkins.get_version()


@pytest.mark.asyncio
async def test_get_status():
    await jenkins.get_status()


@pytest.mark.asyncio
async def test_tokens():
    version = await jenkins.get_version()

    if version.major < 2 or version.minor < 129:
        return

    token_name = test_tokens.__name__
    job_name = test_tokens.__name__

    token_value, token_uuid = await jenkins.generate_token(token_name)

    await jenkins.nodes.enable('master')

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    await jenkins.jobs.create(job_name, JOB_CONFIG_XML)

    # instance without credentials
    jenkins_tokened = Jenkins(JENKINS_HOST, JENKINS_LOGIN, token_value)
    await jenkins_tokened.builds.start(job_name)

    await jenkins.revoke_token(token_uuid)

    with pytest.raises(JenkinsError):
        await jenkins_tokened.builds.start(job_name)

    await jenkins.jobs.delete(job_name)
