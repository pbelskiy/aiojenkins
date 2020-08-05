import contextlib
import time

import pytest

from aiojenkins.exceptions import JenkinsNotFoundError
from tests import CreateJob, jenkins


@pytest.mark.asyncio
async def test_delete_job():
    with contextlib.suppress(JenkinsNotFoundError):
        async with CreateJob() as job_name:
            await jenkins.jobs.delete(job_name)
            available_jobs = await jenkins.jobs.get_all()
            assert job_name not in available_jobs


@pytest.mark.asyncio
async def test_create_job():
    async with CreateJob() as job_name:
        available_jobs = await jenkins.jobs.get_all()
        assert job_name in available_jobs


@pytest.mark.asyncio
async def test_get_job_config():
    async with CreateJob() as job_name:
        config = await jenkins.jobs.get_config(job_name)
        assert len(config) > 0


@pytest.mark.asyncio
async def test_disable_job():
    async with CreateJob() as job_name:
        await jenkins.jobs.disable(job_name)
        job_info = await jenkins.jobs.get_info(job_name)
        assert job_info['color'] == 'disabled'


@pytest.mark.asyncio
async def test_disable_unavailable_job():
    with pytest.raises(JenkinsNotFoundError):
        await jenkins.jobs.disable('unavailable')


@pytest.mark.asyncio
async def test_enable_job():
    async with CreateJob() as job_name:
        await jenkins.jobs.disable(job_name)
        await jenkins.jobs.enable(job_name)
        job_info = await jenkins.jobs.get_info(job_name)
        assert job_info['color'] != 'disabled'


@pytest.mark.asyncio
async def test_get_job_info():
    async with CreateJob() as job_name:
        info = await jenkins.jobs.get_info(job_name)
        assert isinstance(info, dict)


@pytest.mark.asyncio
async def test_copy_job():
    async with CreateJob() as job_name:
        job_name_new = job_name + '_new'
        await jenkins.jobs.copy(job_name, job_name_new)
        try:
            available_jobs = await jenkins.jobs.get_all()
            assert job_name_new in available_jobs
        finally:
            await jenkins.jobs.delete(job_name_new)


@pytest.mark.asyncio
async def test_rename_job():
    async with CreateJob() as job_name:
        job_name_new = job_name + '_new'
        await jenkins.jobs.rename(job_name, job_name_new)
        available_jobs = await jenkins.jobs.get_all()

        assert job_name_new in available_jobs
        assert job_name not in available_jobs

        # for context manager success delete temporary job
        await jenkins.jobs.rename(job_name_new, job_name)


def test_construct_job_config():
    assert len(jenkins.jobs.construct_config()) > 0


@pytest.mark.asyncio
async def test_job_exists():
    # TC: unavailable job must not exist
    assert (await jenkins.jobs.is_exists(str(time.time()))) is False

    # TC: just created job must exist
    async with CreateJob() as job_name:
        assert (await jenkins.jobs.is_exists(job_name)) is True
