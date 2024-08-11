import asyncio
import time

from collections import namedtuple
from http import HTTPStatus

import pytest

from aiojenkins.exceptions import JenkinsError
from aiojenkins.jenkins import Jenkins, JenkinsVersion
from tests import CreateJob, get_host, get_password, get_user, is_ci_server


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


@pytest.mark.skip
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

        token_name = str(time.time_ns())
        token_value, token_uuid = await jenkins.generate_token(token_name)

        await jenkins.nodes.enable('master')

        # instance without credentials
        jenkins_tokened = Jenkins(get_host(), get_user(), token_value)
        await jenkins_tokened.builds.start(job_name)

        await jenkins.revoke_token(token_uuid)

        with pytest.raises(JenkinsError):
            await jenkins_tokened.builds.start(job_name)


@pytest.mark.asyncio
async def test_run_groovy_script(jenkins):
    # TC: compare with expected result
    text = 'test'
    response = await jenkins.run_groovy_script(f'print("{text}")')
    assert response == text

    # TC: invalid script
    response = await jenkins.run_groovy_script('xxx')
    assert 'No such property' in response


@pytest.mark.asyncio
async def test_retry_client(monkeypatch):
    attempts = 0

    async def text():
        return 'error'

    async def request(*args, **kwargs):  # pylint: disable=unused-argument
        nonlocal attempts

        attempts += 1
        response = namedtuple(
            'response', ['status', 'cookies', 'text', 'json']
        )

        if attempts == 1:
            raise asyncio.TimeoutError

        if attempts < 3:
            response.status = HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            response.status = HTTPStatus.OK

        response.text = text
        response.json = text

        return response

    retry = {'total': 5, 'statuses': [HTTPStatus.INTERNAL_SERVER_ERROR]}

    try:
        jenkins = Jenkins(get_host(), get_user(), get_password(), retry=retry)

        await jenkins.get_status()
        monkeypatch.setattr('aiohttp.client.ClientSession.request', request)
        await jenkins.get_status()
    finally:
        await jenkins.close()


@pytest.mark.asyncio
async def test_retry_validation():
    retry = {'attempts': 5, 'statuses': [HTTPStatus.INTERNAL_SERVER_ERROR]}

    with pytest.raises(JenkinsError):
        jenkins = Jenkins(get_host(), get_user(), get_password(), retry=retry)
        await jenkins.get_status()


def test_session_close():

    def do():
        Jenkins(
            get_host(),
            get_user(),
            get_password(),
            retry={'enabled': True},
        )

    do()

    # just check for no exceptions
    import gc
    gc.collect()


@pytest.mark.asyncio
async def test_make_jenkins_version(jenkins, aiohttp_mock):
    jenkins.crumb = False

    aiohttp_mock.get(
        'http://localhost:8080/',
        content_type='text/plain',
        headers={'X-Jenkins': '2.358'},
        status=HTTPStatus.OK,
    )
    version = await jenkins.get_version()
    assert version == JenkinsVersion(major=2, minor=358, patch=0, build=0)

    aiohttp_mock.get(
        'http://localhost:8080/',
        content_type='text/plain',
        headers={'X-Jenkins': '2.358.5'},
        status=HTTPStatus.OK,
    )
    version = await jenkins.get_version()
    assert version == JenkinsVersion(major=2, minor=358, patch=5, build=0)

    aiohttp_mock.get(
        'http://localhost:8080/',
        content_type='text/plain',
        headers={'X-Jenkins': '2.346.1.4'},
        status=HTTPStatus.OK,
    )
    version = await jenkins.get_version()
    assert version == JenkinsVersion(major=2, minor=346, patch=1, build=4)

    await jenkins.close()
