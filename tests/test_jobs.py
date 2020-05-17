import pytest

from aiojenkins.exceptions import JenkinsNotFoundError
from tests import jenkins


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

TEST_JOB_NAME = 'test'


@pytest.mark.asyncio
async def test_delete_job():
    try:
        await jenkins.jobs.delete(TEST_JOB_NAME)
    except JenkinsNotFoundError:
        ...


@pytest.mark.asyncio
async def test_create_job():
    await jenkins.jobs.create(TEST_JOB_NAME, TEST_CONFIG_XML)


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
