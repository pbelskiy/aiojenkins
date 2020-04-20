#!/usr/bin/python3

import os
import asyncio

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


def test_delete_job():
    try:
        asyncio.run(jenkins.delete_job(TEST_JOB_NAME))
    except JenkinsNotFoundError:
        ...


def test_create_job():
    asyncio.run(jenkins.create_job(TEST_JOB_NAME, TEST_CONFIG_XML))


def test_build_job():
    asyncio.run(jenkins.build_job(TEST_JOB_NAME, dict(arg=1, delay=0)))


def test_stop_build():
    asyncio.run(jenkins.stop_build(TEST_JOB_NAME, 1))


def test_get_job_info():
    asyncio.run(jenkins.get_job_info(TEST_JOB_NAME))


def test_get_build_info():
    asyncio.run(jenkins.get_build_info(TEST_JOB_NAME, 1))


def test_delete_build():
    asyncio.run(jenkins.delete_build(TEST_JOB_NAME, 1))


def test_get_status():
    asyncio.run(jenkins.get_nodes())


def test_get_nodes():
    asyncio.run(jenkins.get_nodes())
