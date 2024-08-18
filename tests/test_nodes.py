import asyncio
import contextlib

import pytest

from aiojenkins.exceptions import JenkinsError, JenkinsNotFoundError
from aiojenkins.utils import construct_node_config
from tests import CreateJob


async def test_get_nodes(jenkins):
    await jenkins.nodes.get_all()


async def test_get_node_info(jenkins):
    info = await jenkins.nodes.get_info('(master)')
    assert isinstance(info, dict)
    info = await jenkins.nodes.get_info('master')
    assert isinstance(info, dict)


async def test_is_node_exists(jenkins):
    is_exists = await jenkins.nodes.is_exists('master')
    assert is_exists is True

    is_exists = await jenkins.nodes.is_exists('random_empty_node')
    assert is_exists is False

    is_exists = await jenkins.nodes.is_exists('')
    assert is_exists is False


async def test_disable_node(jenkins):
    for _ in range(2):
        await jenkins.nodes.disable('master')
        info = await jenkins.nodes.get_info('master')
        assert info['offline'] is True


async def test_enable_node(jenkins):
    for _ in range(2):
        await jenkins.nodes.enable('master')
        info = await jenkins.nodes.get_info('master')
        assert info['offline'] is False


async def test_update_node_offline_reason(jenkins):
    await jenkins.nodes.update_offline_reason('master', 'maintenance1')
    info = await jenkins.nodes.get_info('master')
    assert info['offlineCauseReason'] == 'maintenance1'

    await jenkins.nodes.update_offline_reason('master', 'maintenance2')
    info = await jenkins.nodes.get_info('master')
    assert info['offlineCauseReason'] == 'maintenance2'


async def test_get_node_config(jenkins):
    TEST_NODE_NAME = test_get_node_config.__name__

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.nodes.delete(TEST_NODE_NAME)

    with pytest.raises(JenkinsNotFoundError):
        await jenkins.nodes.get_config(TEST_NODE_NAME)

    config = jenkins.nodes.construct(name=TEST_NODE_NAME)
    await jenkins.nodes.create(TEST_NODE_NAME, config)
    await asyncio.sleep(3)

    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME in nodes_list

    # TC: correct config must be received
    received_config = await jenkins.nodes.get_config(TEST_NODE_NAME)
    assert len(received_config) > 0
    await jenkins.nodes.delete(TEST_NODE_NAME)


async def test_node_reconfigure(jenkins):
    TEST_NODE_NAME = test_node_reconfigure.__name__

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.nodes.delete(TEST_NODE_NAME)

    config = jenkins.nodes.construct(name=TEST_NODE_NAME)
    await jenkins.nodes.create(TEST_NODE_NAME, config)
    await asyncio.sleep(3)

    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME in nodes_list

    old_config = await jenkins.nodes.get_config(TEST_NODE_NAME)
    new_config = old_config.replace(
        '<numExecutors>2</numExecutors>',
        '<numExecutors>4</numExecutors>'
    )

    await jenkins.nodes.reconfigure(TEST_NODE_NAME, new_config)
    config = await jenkins.nodes.get_config(TEST_NODE_NAME)
    assert '<numExecutors>4</numExecutors>' in config

    await jenkins.nodes.delete(TEST_NODE_NAME)


async def test_node_reconfigure_master(jenkins):
    config = jenkins.nodes.construct(name='reconfigure_master')

    with pytest.raises(JenkinsError):
        await jenkins.nodes.reconfigure('master', config)


async def test_create_delete_node(jenkins):
    TEST_NODE_NAME = test_create_delete_node.__name__

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.nodes.delete(TEST_NODE_NAME)

    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME not in nodes_list

    config = construct_node_config(name=TEST_NODE_NAME)
    await jenkins.nodes.create(TEST_NODE_NAME, config)
    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME in nodes_list

    with pytest.raises(JenkinsError):
        await jenkins.nodes.create(TEST_NODE_NAME, config)

    await jenkins.nodes.delete(TEST_NODE_NAME)
    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME not in nodes_list


async def test_get_all_builds(jenkins):
    node_name = 'master'
    await jenkins.nodes.enable(node_name)

    async with CreateJob(jenkins) as job_name:
        await jenkins.builds.start(job_name)
        await asyncio.sleep(1)

        builds = await jenkins.nodes.get_all_builds(node_name)
        assert len(builds) > 0

        assert builds[-1]['job_name'] == job_name


async def test_get_failed_builds(jenkins):
    node_name = 'master'
    await jenkins.nodes.enable(node_name)

    async with CreateJob(jenkins, commands=['false']) as job_name:
        pre_failed_builds = await jenkins.nodes.get_failed_builds(node_name)

        await jenkins.builds.start(job_name)
        await asyncio.sleep(1)

        post_failed_builds = await jenkins.nodes.get_failed_builds(node_name)
        assert (len(post_failed_builds) - len(pre_failed_builds)) > 0

        assert post_failed_builds[-1]['job_name'] == job_name
