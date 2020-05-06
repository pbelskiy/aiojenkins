#!/usr/bin/python3

import asyncio
import contextlib
import os

import pytest

from aiojenkins import Jenkins, JenkinsError, JenkinsNotFoundError

HOST_ADDR = os.environ.get('host', 'http://localhost:8080')

jenkins = Jenkins(
    HOST_ADDR,
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
async def test_authentication_error():
    with pytest.raises(JenkinsError):
        await Jenkins(HOST_ADDR, 'random-login', 'random-password').get_status()


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
    info = await jenkins.get_job_info(TEST_JOB_NAME)
    assert info['nextBuildNumber'] == 2

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
    info = await jenkins.get_job_info(TEST_JOB_NAME)
    assert isinstance(info, dict)


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


@pytest.mark.asyncio
async def test_create_delete_node():
    TEST_NODE_NAME = 'test_node'

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.delete_node(TEST_NODE_NAME)

    nodes_list = await jenkins.get_nodes()
    assert TEST_NODE_NAME not in nodes_list

    config = {
        'name': TEST_NODE_NAME,
        'nodeDescription': '',
        'numExecutors': 10,
        'remoteFS': '',
        'labelString': '',
        'launcher': {
            'stapler-class': 'hudson.slaves.JNLPLauncher',
        },
        'retentionStrategy': {
            'stapler-class': 'hudson.slaves.RetentionStrategy$Always',
        },
        'nodeProperties': {
            'stapler-class-bag': 'true'
        }
    }

    await jenkins.create_node(TEST_NODE_NAME, config)
    nodes_list = await jenkins.get_nodes()
    assert TEST_NODE_NAME in nodes_list

    with pytest.raises(JenkinsError):
        await jenkins.create_node(TEST_NODE_NAME, config)

    await jenkins.delete_node(TEST_NODE_NAME)
    nodes_list = await jenkins.get_nodes()
    assert TEST_NODE_NAME not in nodes_list
