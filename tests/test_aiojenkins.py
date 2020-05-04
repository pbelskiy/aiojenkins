#!/usr/bin/python3

import os
import asyncio

import pytest

from aiojenkins import Jenkins, JenkinsNotFoundError

jenkins = Jenkins(
    'http://localhost:8080',
    os.environ.get('login', 'admin'),
    os.environ.get('password', 'admin')
)

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
        await jenkins.delete_job(TEST_JOB_NAME)
    except JenkinsNotFoundError:
        ...


@pytest.mark.asyncio
async def test_create_job():
    await jenkins.create_job(TEST_JOB_NAME, TEST_CONFIG_XML)


@pytest.mark.asyncio
async def test_get_job_config():
    await jenkins.get_job_config(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_build_job():
    await jenkins.enable_node('master')
    await jenkins.build_job(TEST_JOB_NAME, dict(delay=0))
    await jenkins.build_job(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_disable_job():
    await jenkins.disable_job(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_disable_unavailable_job():
    with pytest.raises(JenkinsNotFoundError):
        await jenkins.disable_job('unavailable')


@pytest.mark.asyncio
async def test_enable_job():
    await jenkins.enable_job(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_stop_build():
    await jenkins.stop_build(TEST_JOB_NAME, 1)


@pytest.mark.asyncio
async def test_get_job_info():
    await jenkins.get_job_info(TEST_JOB_NAME)


@pytest.mark.asyncio
async def test_get_build_info():
    await jenkins.get_build_info(TEST_JOB_NAME, 1)


@pytest.mark.asyncio
async def test_delete_build():
    await jenkins.delete_build(TEST_JOB_NAME, 1)


@pytest.mark.asyncio
async def test_get_status():
    await jenkins.get_status()


@pytest.mark.asyncio
async def test_get_nodes():
    await jenkins.get_nodes()


@pytest.mark.asyncio
async def test_get_node_info():
    info = await jenkins.get_node_info('(master)')
    assert isinstance(info, dict)
    info = await jenkins.get_node_info('master')
    assert isinstance(info, dict)


@pytest.mark.asyncio
async def test_is_node_exists():
    is_exists = await jenkins.is_node_exists('master')
    assert is_exists is True

    is_exists = await jenkins.is_node_exists('random_empty_node')
    assert is_exists is False

    is_exists = await jenkins.is_node_exists('')
    assert is_exists is False


@pytest.mark.asyncio
async def test_disable_node():
    for _ in range(2):
        await jenkins.disable_node('master')
        info = await jenkins.get_node_info('master')
        assert info['offline'] is True


@pytest.mark.asyncio
async def test_enable_node():
    for _ in range(2):
        await jenkins.enable_node('master')
        info = await jenkins.get_node_info('master')
        assert info['offline'] is False


@pytest.mark.asyncio
async def test_update_node_offline_reason():
    await jenkins.update_node_offline_reason('master', 'maintenance1')
    info = await jenkins.get_node_info('master')
    assert info['offlineCauseReason'] == 'maintenance1'

    await jenkins.update_node_offline_reason('master', 'maintenance2')
    info = await jenkins.get_node_info('master')
    assert info['offlineCauseReason'] == 'maintenance2'
