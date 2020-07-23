import time

import pytest

from aiojenkins.exceptions import JenkinsNotFoundError
from aiojenkins.utils import construct_job_config
from tests import CreateJob, jenkins

TEST_JOB_NAME = 'test'


@pytest.mark.asyncio
async def test_delete_job():
    try:
        await jenkins.jobs.delete(TEST_JOB_NAME)
    except JenkinsNotFoundError:
        ...


@pytest.mark.asyncio
async def test_create_job():
    await jenkins.jobs.create(TEST_JOB_NAME, construct_job_config())


@pytest.mark.asyncio
async def test_get_job_config():
    await jenkins.jobs.get_config(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_disable_job():
    await jenkins.jobs.disable(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_disable_unavailable_job():
    with pytest.raises(JenkinsNotFoundError):
        await jenkins.jobs.disable('unavailable')


@pytest.mark.asyncio
async def test_enable_job():
    await jenkins.jobs.enable(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_get_job_info():
    info = await jenkins.jobs.get_info(TEST_JOB_NAME)
    assert isinstance(info, dict)


@pytest.mark.asyncio
async def test_copy_job():
    async with CreateJob() as job_name:
        job_name_new = f'{job_name}_new'
        await jenkins.jobs.copy(job_name, job_name_new)
        available_jobs = await jenkins.jobs.get_all()
        assert job_name_new in available_jobs


@pytest.mark.asyncio
async def test_rename_job():
    async with CreateJob() as job_name:
        job_name_new = f'{job_name}_new'
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
