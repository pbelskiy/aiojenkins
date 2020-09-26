import asyncio
import time

from collections import namedtuple
from http import HTTPStatus

import pytest

from aiojenkins import Jenkins
from aiojenkins.exceptions import JenkinsError
from tests import CreateJob, get_host, get_login, get_password, is_ci_server


@pytest.mark.asyncio
async def test_invalid_host(jenkins):
    with pytest.raises(JenkinsError):
        jenkins = Jenkins('@#$')
        await jenkins.get_version()


@pytest.mark.asyncio
async def test_get_status(jenkins):
    await jenkins.get_status()


@pytest.mark.asyncio
async def test_quiet_down(jenkins):
    await jenkins.quiet_down()
    server_status = await jenkins.get_status()
    assert server_status['quietingDown'] is True

    await jenkins.cancel_quiet_down()
    server_status = await jenkins.get_status()
    assert server_status['quietingDown'] is False


@pytest.mark.asyncio
async def test_restart(jenkins):
    if not is_ci_server():
        pytest.skip('takes too much time +40 seconds')

    await jenkins.safe_restart()
    await asyncio.sleep(5)

    await jenkins.wait_until_ready()
    assert (await jenkins.is_ready()) is True

    await jenkins.restart()
    await jenkins.wait_until_ready()
    assert (await jenkins.is_ready()) is True


@pytest.mark.asyncio
async def test_tokens(jenkins):
    version = await jenkins.get_version()

    if not (version.major >= 2 and version.minor >= 129):
        pytest.skip('Version isn`t support API tokens')

    async with CreateJob(jenkins) as job_name:
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
async def test_run_groovy_script(jenkins):
    # TC: compare with expected result
    text = 'test'
    response = await jenkins.run_groovy_script('print("{}")'.format(text))
    assert response == text

    # TC: invalid script
    response = await jenkins.run_groovy_script('xxx')
    assert 'No such property' in response


@pytest.mark.asyncio
async def test_retry_client(monkeypatch):
    attempts = 0

    async def text():
        return 'error'

    async def request(*args, **kwargs):
        nonlocal attempts

        attempts += 1
        response = namedtuple(
            'response', ['status', 'cookies', 'text', 'json']
        )

        if attempts < 3:
            response.status = HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            response.status = HTTPStatus.OK

        response.text = text
        response.json = text

        return response

    retry = dict(
        enabled=True,
        attempts=5,
        interval=0.01,
    )

    retry_jenkins = Jenkins(
        get_host(),
        get_login(),
        get_password(),
        retry=retry
    )

    await retry_jenkins.get_status()
    monkeypatch.setattr('aiohttp.client.ClientSession.request', request)
    await retry_jenkins.get_status()


def test_session_close():

    def do():
        Jenkins(
            get_host(),
            get_login(),
            get_password(),
            retry=dict(enabled=True)
        )

    do()

    # just check for no exceptions
    import gc
    gc.collect()
