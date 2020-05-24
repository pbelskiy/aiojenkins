import contextlib

import pytest

from aiojenkins.exceptions import JenkinsError, JenkinsNotFoundError
from tests import jenkins


@pytest.mark.asyncio
async def test_get_nodes():
    await jenkins.nodes.get_all()


@pytest.mark.asyncio
async def test_get_node_info():
    info = await jenkins.nodes.get_info('(master)')
    assert isinstance(info, dict)
    info = await jenkins.nodes.get_info('master')
    assert isinstance(info, dict)


@pytest.mark.asyncio
async def test_is_node_exists():
    is_exists = await jenkins.nodes.is_exists('master')
    assert is_exists is True

    is_exists = await jenkins.nodes.is_exists('random_empty_node')
    assert is_exists is False

    is_exists = await jenkins.nodes.is_exists('')
    assert is_exists is False


@pytest.mark.asyncio
async def test_disable_node():
    for _ in range(2):
        await jenkins.nodes.disable('master')
        info = await jenkins.nodes.get_info('master')
        assert info['offline'] is True


@pytest.mark.asyncio
async def test_enable_node():
    for _ in range(2):
        await jenkins.nodes.enable('master')
        info = await jenkins.nodes.get_info('master')
        assert info['offline'] is False


@pytest.mark.asyncio
async def test_update_node_offline_reason():
    await jenkins.nodes.update_offline_reason('master', 'maintenance1')
    info = await jenkins.nodes.get_info('master')
    assert info['offlineCauseReason'] == 'maintenance1'

    await jenkins.nodes.update_offline_reason('master', 'maintenance2')
    info = await jenkins.nodes.get_info('master')
    assert info['offlineCauseReason'] == 'maintenance2'


@pytest.mark.asyncio
async def test_create_delete_node():
    TEST_NODE_NAME = 'test_node'

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.nodes.delete(TEST_NODE_NAME)

    nodes_list = await jenkins.nodes.get_all()
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

    await jenkins.nodes.create(TEST_NODE_NAME, config)
    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME in nodes_list

    with pytest.raises(JenkinsError):
        await jenkins.nodes.create(TEST_NODE_NAME, config)

    await jenkins.nodes.delete(TEST_NODE_NAME)
    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME not in nodes_list
