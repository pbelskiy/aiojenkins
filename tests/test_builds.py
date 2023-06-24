import asyncio

import pytest

from aiojenkins.exceptions import JenkinsError
from tests import CreateJob


@pytest.mark.asyncio
async def test_build_start(jenkins):
    arg_name = 'arg'
    arg_value = 'arg'

    config = dict(
        parameters=[dict(name=arg_name)]
    )

    async with CreateJob(jenkins, **config) as job_name:
        await jenkins.builds.start(job_name, {arg_name: arg_value})
        await asyncio.sleep(1)

        job_info = await jenkins.jobs.get_info(job_name)
        last_build_number = job_info['lastBuild']['number']

        build_info = await jenkins.builds.get_info(job_name, last_build_number)
        assert build_info['actions'][0]['parameters'][0]['value'] == arg_value


@pytest.mark.asyncio
async def test_build_list(jenkins):
    async with CreateJob(jenkins, parameters=[dict(name='arg')]) as job_name:
        # TC: just created job must not has any builds
        builds = await jenkins.builds.get_all(job_name)
        assert len(builds) == 0

        # TC: build list must contain something after build triggered
        await jenkins.nodes.enable('master')
        await jenkins.builds.start(job_name, dict(arg=0))

        info = await jenkins.jobs.get_info(job_name)
        builds = await jenkins.builds.get_all(job_name)
        assert (info['inQueue'] is True or len(builds) > 0)

        if not info['inQueue']:
            last_build_id = builds[-1]['number']
            output = await jenkins.builds.get_output(job_name, last_build_id)
            assert len(output) > 0


@pytest.mark.asyncio
async def test_build_stop_delete(jenkins):
    job_config = dict(
        parameters=[dict(name='arg')],
        commands=['echo 1', 'echo 2']
    )

    async with CreateJob(jenkins, **job_config) as job_name:
        await jenkins.nodes.enable('master')

        await jenkins.builds.start(job_name, dict(arg='test'))
        await asyncio.sleep(1)

        info = await jenkins.jobs.get_info(job_name)
        assert info['nextBuildNumber'] == 2

        # parameters must be passed
        with pytest.raises(JenkinsError):
            await jenkins.builds.start(job_name)

        with pytest.raises(JenkinsError):
            await jenkins.builds.start(job_name, delay=1)

        await jenkins.builds.stop(job_name, 1)
        await jenkins.builds.get_info(job_name, 1)
        await jenkins.builds.delete(job_name, 1)


@pytest.mark.asyncio
async def test_build_exists(jenkins):
    async with CreateJob(jenkins) as job_name:
        # TC: just created job hasn't any builds yet
        assert (await jenkins.builds.is_exists(job_name, 1)) is False

        # TC: start build and check its existence
        await jenkins.builds.start(job_name)
        await asyncio.sleep(1)

        assert (await jenkins.builds.is_exists(job_name, 1)) is True


@pytest.mark.asyncio
async def test_build_queue_id(jenkins):
    async with CreateJob(jenkins) as job_name:
        queue_id = await jenkins.builds.start(job_name)
        assert queue_id > 0

        queue_id_info = await jenkins.builds.get_queue_id_info(queue_id)
        assert isinstance(queue_id_info, dict) is True


@pytest.mark.asyncio
async def test_build_get_url_info(jenkins):
    # TC: invalid URL must raise the exception
    with pytest.raises(JenkinsError):
        await jenkins.builds.get_url_info('invalid')

    # TC: correct build url must return info (dict)
    async with CreateJob(jenkins) as job_name:
        await jenkins.builds.start(job_name)
        await asyncio.sleep(1)

        job_info = await jenkins.jobs.get_info(job_name)
        build_url = job_info['builds'][-1]['url']

        build_info = await jenkins.builds.get_url_info(build_url)
        assert isinstance(build_info, dict) is True


@pytest.mark.asyncio
async def test_build_delay(jenkins):
    async with CreateJob(jenkins) as job_name:
        await jenkins.nodes.enable('master')
        await jenkins.builds.start(job_name, delay=2)

        await asyncio.sleep(1.5)
        info = await jenkins.jobs.get_info(job_name)
        builds = await jenkins.builds.get_all(job_name)
        assert (info['inQueue'] is True and len(builds) == 0)
