import contextlib
import time

import pytest

from aiojenkins.exceptions import JenkinsNotFoundError
from tests import CreateJob


@pytest.mark.asyncio
async def test_delete_job(jenkins):
    with contextlib.suppress(JenkinsNotFoundError):
        async with CreateJob(jenkins) as job_name:
            await jenkins.jobs.delete(job_name)
            available_jobs = await jenkins.jobs.get_all()
            assert job_name not in available_jobs


@pytest.mark.asyncio
async def test_create_job(jenkins):
    async with CreateJob(jenkins) as job_name:
        available_jobs = await jenkins.jobs.get_all()
        assert job_name in available_jobs


@pytest.mark.asyncio
async def test_get_job_config(jenkins):
    async with CreateJob(jenkins) as job_name:
        config = await jenkins.jobs.get_config(job_name)
        assert len(config) > 0


@pytest.mark.asyncio
async def test_get_job_reconfigure(jenkins):
    async with CreateJob(jenkins) as job_name:
        config_old = await jenkins.jobs.get_config(job_name)

        config_new = config_old.replace(
            '<concurrentBuild>false</concurrentBuild>',
            '<concurrentBuild>true</concurrentBuild>'
        )

        await jenkins.jobs.reconfigure(job_name, config_new)
        config = await jenkins.jobs.get_config(job_name)
        assert '<concurrentBuild>true</concurrentBuild>' in config


@pytest.mark.asyncio
async def test_disable_job(jenkins):
    async with CreateJob(jenkins) as job_name:
        await jenkins.jobs.disable(job_name)
        job_info = await jenkins.jobs.get_info(job_name)
        assert job_info['color'] == 'disabled'


@pytest.mark.asyncio
async def test_disable_unavailable_job(jenkins):
    with pytest.raises(JenkinsNotFoundError):
        await jenkins.jobs.disable('unavailable')


@pytest.mark.asyncio
async def test_enable_job(jenkins):
    async with CreateJob(jenkins) as job_name:
        await jenkins.jobs.disable(job_name)
        await jenkins.jobs.enable(job_name)
        job_info = await jenkins.jobs.get_info(job_name)
        assert job_info['color'] != 'disabled'


@pytest.mark.asyncio
async def test_get_job_info(jenkins):
    async with CreateJob(jenkins) as job_name:
        info = await jenkins.jobs.get_info(job_name)
        assert isinstance(info, dict)


@pytest.mark.asyncio
async def test_copy_job(jenkins):
    async with CreateJob(jenkins) as job_name:
        job_name_new = job_name + '_new'
        await jenkins.jobs.copy(job_name, job_name_new)
        try:
            available_jobs = await jenkins.jobs.get_all()
            assert job_name_new in available_jobs
        finally:
            await jenkins.jobs.delete(job_name_new)


@pytest.mark.asyncio
async def test_rename_job(jenkins):
    async with CreateJob(jenkins) as job_name:
        job_name_new = job_name + '_new'
        await jenkins.jobs.rename(job_name, job_name_new)
        available_jobs = await jenkins.jobs.get_all()

        assert job_name_new in available_jobs
        assert job_name not in available_jobs

        # for context manager success delete temporary job
        await jenkins.jobs.rename(job_name_new, job_name)


def test_construct_job_config(jenkins):
    assert len(jenkins.jobs.construct_config()) > 0


@pytest.mark.asyncio
async def test_job_exists(jenkins):
    # TC: unavailable job must not exist
    assert (await jenkins.jobs.is_exists(str(time.time()))) is False

    # TC: just created job must exist
    async with CreateJob(jenkins) as job_name:
        assert (await jenkins.jobs.is_exists(job_name)) is True
