import contextlib
import pytest

from aiojenkins.exceptions import (
    JenkinsError,
    JenkinsNotFoundError,
)

from aiojenkins.utils import construct_job_config

from tests import jenkins


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
    job_name_old = test_copy_job.__name__
    job_name_new = job_name_old + '_new'

    with contextlib.suppress(JenkinsError):
        await jenkins.jobs.delete(job_name_old)
        await jenkins.jobs.delete(job_name_new)

    await jenkins.jobs.create(job_name_old, construct_job_config())
    available_jobs = await jenkins.jobs.get_all()
    assert job_name_old in available_jobs

    await jenkins.jobs.copy(job_name_old, job_name_new)
    available_jobs = await jenkins.jobs.get_all()

    assert job_name_new in available_jobs
    assert job_name_old in available_jobs

    await jenkins.jobs.delete(job_name_old)
    await jenkins.jobs.delete(job_name_new)


@pytest.mark.asyncio
async def test_rename_job():
    job_name_old = test_rename_job.__name__
    job_name_new = job_name_old + '_new'

    with contextlib.suppress(JenkinsError):
        await jenkins.jobs.delete(job_name_old)
        await jenkins.jobs.delete(job_name_new)

    await jenkins.jobs.create(job_name_old, jenkins.jobs.construct())
    available_jobs = await jenkins.jobs.get_all()
    assert job_name_old in available_jobs

    await jenkins.jobs.rename(job_name_old, job_name_new)
    available_jobs = await jenkins.jobs.get_all()

    assert job_name_new in available_jobs
    assert job_name_old not in available_jobs

    await jenkins.jobs.delete(job_name_new)


def test_construct_job_config():
    assert len(construct_job_config()) > 0
