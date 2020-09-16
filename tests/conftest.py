import pytest

from aiojenkins import Jenkins
from tests import get_host, get_login, get_password


@pytest.fixture
def jenkins():
    return Jenkins(get_host(), get_login(), get_password())
