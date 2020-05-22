import contextlib
import pytest

from aiojenkins.exceptions import (
    JenkinsError,
    JenkinsNotFoundError,
)

from tests import (
    generate_job_config,
    jenkins,
)


@pytest.mark.asyncio
async def test_build_list():
    job_name = test_build_list.__name__

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    await jenkins.jobs.create(job_name, generate_job_config(['arg']))

    builds = await jenkins.builds.get_list(job_name)
    assert len(builds) == 0

    await jenkins.nodes.enable('master')

    # NB: on Jenkins ~1.554 job without arguments has some internal delay
    await jenkins.builds.start(job_name, dict(arg=0))

    builds = await jenkins.builds.get_list(job_name)
    assert len(builds) > 0

    output = await jenkins.builds.get_output(job_name, builds[-1]['number'])
    assert len(output) > 0

    await jenkins.jobs.delete(job_name)


@pytest.mark.asyncio
async def test_build_machinery():
    job_name = test_build_machinery.__name__

    await jenkins.nodes.enable('master')

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    job_config = generate_job_config(['arg'])

    await jenkins.jobs.create(job_name, job_config)

    await jenkins.builds.start(job_name, dict(arg='test'))
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
