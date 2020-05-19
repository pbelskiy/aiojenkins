import contextlib
import pytest

from aiojenkins.exceptions import (
    JenkinsError,
    JenkinsNotFoundError,
)
from tests import jenkins


TEST_JOB_NAME = 'test_builds'

TEST_CONFIG_XML = """<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.StringParameterDefinition>
          <name>arg</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command></command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>
"""


@pytest.mark.asyncio
async def test_build_list():
    job_name = test_build_list.__name__

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    await jenkins.jobs.create(job_name, TEST_CONFIG_XML)

    builds = await jenkins.builds.get_list(job_name)
    assert len(builds) == 0

    await jenkins.nodes.enable('master')
    await jenkins.builds.start(job_name, dict(arg=0))

    builds = await jenkins.builds.get_list(job_name)
    assert len(builds) > 0

    output = await jenkins.builds.get_output(job_name, builds[-1]['number'])
    assert len(output) > 0

    await jenkins.jobs.delete(job_name)


@pytest.mark.asyncio
async def test_build_start():
    await jenkins.nodes.enable('master')

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(TEST_JOB_NAME)

    await jenkins.jobs.create(TEST_JOB_NAME, TEST_CONFIG_XML)

    await jenkins.builds.start(TEST_JOB_NAME, dict(arg='test'))
    info = await jenkins.jobs.get_info(TEST_JOB_NAME)
    assert info['nextBuildNumber'] == 2

    await jenkins.builds.start(TEST_JOB_NAME)

    await jenkins.builds.start(TEST_JOB_NAME, delay=1)

    with pytest.raises(JenkinsError):
        await jenkins.builds.start(TEST_JOB_NAME, dict(delay=0))
        await jenkins.builds.start(TEST_JOB_NAME, dict(no_parameter='none'))


@pytest.mark.asyncio
async def test_build_stop():
    await jenkins.builds.stop(TEST_JOB_NAME, 1)


@pytest.mark.asyncio
async def test_get_build_info():
    await jenkins.builds.get_info(TEST_JOB_NAME, 1)


@pytest.mark.asyncio
async def test_delete_build():
    await jenkins.builds.delete(TEST_JOB_NAME, 1)
