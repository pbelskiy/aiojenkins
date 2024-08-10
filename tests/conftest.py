import pytest

from aioresponses import aioresponses

from aiojenkins.jenkins import Jenkins
from tests import get_host, get_password, get_user


@pytest.fixture
async def jenkins():  # pylint: disable=redefined-outer-name
    async with Jenkins(get_host(), get_user(), get_password()) as client:
        yield client


@pytest.fixture
def aiohttp_mock():
    with aioresponses() as mock:
        yield mock
