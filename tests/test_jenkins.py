import asyncio
import time

import pytest

from aiojenkins import Jenkins
from aiojenkins.exceptions import JenkinsError
from tests import CreateJob, get_host, get_login, is_locally, jenkins


@pytest.mark.asyncio
async def test_authentication_error():
    jenkins = Jenkins(get_host(), 'random-login', 'random-password')

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
async def test_quiet_down():
    await jenkins.quiet_down()
    server_status = await jenkins.get_status()
    assert server_status['quietingDown'] is True

    await jenkins.cancel_quiet_down()
    server_status = await jenkins.get_status()
    assert server_status['quietingDown'] is False


@pytest.mark.asyncio
async def test_restart():
    if is_locally():
        pytest.skip('takes too much time +40 seconds')

    await jenkins.safe_restart()
    await asyncio.sleep(5)

    await jenkins.wait_until_ready()
    assert (await jenkins.is_ready()) is True

    await jenkins.restart()
    await jenkins.wait_until_ready()
    assert (await jenkins.is_ready()) is True


@pytest.mark.asyncio
async def test_tokens():
    version = await jenkins.get_version()

    if not (version.major >= 2 and version.minor >= 129):
        pytest.skip('Version isn`t support API tokens')

    async with CreateJob() as job_name:
        token_value, token_uuid = await jenkins.generate_token('')

        token_name = str(time.time())
        token_value, token_uuid = await jenkins.generate_token(token_name)

        await jenkins.nodes.enable('master')

        # instance without credentials
        jenkins_tokened = Jenkins(get_host(), get_login(), token_value)
        await jenkins_tokened.builds.start(job_name)

        await jenkins.revoke_token(token_uuid)

        with pytest.raises(JenkinsError):
            await jenkins_tokened.builds.start(job_name)


@pytest.mark.asyncio
async def test_run_groovy_script():
    # TC: compare with expected result
    text = 'test'
    response = await jenkins.run_groovy_script('print("{}")'.format(text))
    assert response == text

    # TC: invalid script
    response = await jenkins.run_groovy_script('xxx')
    assert 'No such property' in response
