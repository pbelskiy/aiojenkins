import asyncio
import contextlib
import time

import pytest

from aiojenkins.exceptions import (
    JenkinsError,
    JenkinsNotFoundError,
)

from aiojenkins.utils import construct_job_config

from tests import jenkins


@pytest.mark.asyncio
async def test_build_list():
    job_name = f'{test_build_list.__name__}_{time.time()}'

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    await jenkins.jobs.create(
        job_name, construct_job_config(
            parameters=[dict(name='arg')]
        )
    )

    builds = await jenkins.builds.get_all(job_name)
    assert len(builds) == 0

    await jenkins.nodes.enable('master')
    await jenkins.builds.start(job_name, dict(arg=0))

    info = await jenkins.jobs.get_info(job_name)
    builds = await jenkins.builds.get_all(job_name)
    assert (info['inQueue'] is True or len(builds) > 0)

    if not info['inQueue']:
        last_build_id = builds[-1]['number']
        output = await jenkins.builds.get_output(job_name, last_build_id)
        assert len(output) > 0

    await jenkins.jobs.delete(job_name)
    with pytest.raises(JenkinsNotFoundError):
        await jenkins.jobs.get_info(job_name)


@pytest.mark.asyncio
async def test_build_machinery():
    job_name = f'{test_build_machinery.__name__}_{time.time()}'

    await jenkins.nodes.enable('master')

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    job_config = construct_job_config(
        parameters=[dict(name='arg')],
        commands=['echo 1', 'echo 2']
    )

    await jenkins.jobs.create(job_name, job_config)

    await jenkins.builds.start(job_name, dict(arg='test'))
    await asyncio.sleep(1)

    info = await jenkins.jobs.get_info(job_name)
    assert info['nextBuildNumber'] == 2

    # parameters must be passed
    with pytest.raises(JenkinsError):
        await jenkins.builds.start(job_name)
        await jenkins.builds.start(job_name, delay=1)

    with pytest.raises(JenkinsError):
        await jenkins.builds.start(job_name, dict(delay=0))
        await jenkins.builds.start(job_name, dict(no_parameter='none'))

    await jenkins.builds.stop(job_name, 1)
    await jenkins.builds.get_info(job_name, 1)
    await jenkins.builds.delete(job_name, 1)

    await jenkins.jobs.delete(job_name)
    with pytest.raises(JenkinsNotFoundError):
        await jenkins.jobs.get_info(job_name)
