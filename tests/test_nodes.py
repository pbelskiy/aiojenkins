import asyncio
import contextlib
import time

import pytest

from aiojenkins.exceptions import JenkinsError, JenkinsNotFoundError
from aiojenkins.utils import construct_job_config
from tests import jenkins


# TODO: move to utils as job config constructor
def construct_node_config(name: str) -> dict:
    return {
        'name': name,
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
async def test_get_node_config():
    TEST_NODE_NAME = test_get_node_config.__name__

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.nodes.delete(TEST_NODE_NAME)

    with pytest.raises(JenkinsNotFoundError):
        await jenkins.nodes.get_config(TEST_NODE_NAME)

    config = construct_node_config(TEST_NODE_NAME)
    await jenkins.nodes.create(TEST_NODE_NAME, config)

    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME in nodes_list

    # FIXME: timeout error only on github actions
    # received_config = await jenkins.nodes.get_config(TEST_NODE_NAME)
    # assert len(received_config) > 0


@pytest.mark.asyncio
async def test_create_delete_node():
    TEST_NODE_NAME = test_create_delete_node.__name__

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.nodes.delete(TEST_NODE_NAME)

    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME not in nodes_list

    config = construct_node_config(TEST_NODE_NAME)
    await jenkins.nodes.create(TEST_NODE_NAME, config)
    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME in nodes_list

    with pytest.raises(JenkinsError):
        await jenkins.nodes.create(TEST_NODE_NAME, config)

    await jenkins.nodes.delete(TEST_NODE_NAME)
    nodes_list = await jenkins.nodes.get_all()
    assert TEST_NODE_NAME not in nodes_list


@pytest.mark.asyncio
async def test_get_all_builds():
    job_name = f'{test_get_all_builds.__name__}_{time.time()}'
    node_name = 'master'

    await jenkins.nodes.enable(node_name)

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    job_config = construct_job_config()

    await jenkins.jobs.create(job_name, job_config)

    await jenkins.builds.start(job_name)
    await asyncio.sleep(1)  # FIXME:

    builds = await jenkins.nodes.get_all_builds(node_name)
    assert len(builds) > 0

    assert builds[-1]['job_name'] == job_name

    await jenkins.jobs.delete(job_name)


@pytest.mark.asyncio
async def test_get_failed_builds():
    job_name = f'{test_get_failed_builds.__name__}_{time.time()}'
    node_name = 'master'

    await jenkins.nodes.enable(node_name)

    with contextlib.suppress(JenkinsNotFoundError):
        await jenkins.jobs.delete(job_name)

    job_config = construct_job_config(commands=['false'])

    await jenkins.jobs.create(job_name, job_config)

    pre_failed_builds = await jenkins.nodes.get_failed_builds(node_name)

    await jenkins.builds.start(job_name)
    await asyncio.sleep(1)  # FIXME:

    post_failed_builds = await jenkins.nodes.get_failed_builds(node_name)
    assert (len(post_failed_builds) - len(pre_failed_builds)) > 0

    assert post_failed_builds[-1]['job_name'] == job_name

    await jenkins.jobs.delete(job_name)
