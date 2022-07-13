import asyncio

import pytest

from aiojenkins.jenkins import Jenkins
from tests import get_host, get_password, get_user


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def jenkins(event_loop):
    async def _create_jenkins():
        return Jenkins(get_host(), get_user(), get_password())

    jenkins = event_loop.run_until_complete(_create_jenkins())
    yield jenkins

    async def _close_jenkins():
        await jenkins.close()

    event_loop.run_until_complete(_close_jenkins())
