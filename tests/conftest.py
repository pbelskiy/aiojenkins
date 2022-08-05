import asyncio

import pytest

from aioresponses import aioresponses

from aiojenkins.jenkins import Jenkins
from tests import get_host, get_password, get_user


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def jenkins(event_loop):  # pylint: disable=redefined-outer-name
    async def _create_client():
        return Jenkins(get_host(), get_user(), get_password())

    async def _close_client():
        await client.close()

    client = event_loop.run_until_complete(_create_client())
    yield client
    event_loop.run_until_complete(_close_client())


@pytest.fixture
def aiohttp_mock():
    with aioresponses() as mock:
        yield mock
