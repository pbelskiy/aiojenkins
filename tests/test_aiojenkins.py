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
      <command>echo test $arg
sleep 1000</command>
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
    await jenkins.build_job(TEST_JOB_NAME, dict(arg=1, delay=0))


@pytest.mark.asyncio
async def test_disable_job():
    await jenkins.disable_job(TEST_JOB_NAME)


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
