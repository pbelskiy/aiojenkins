import pytest

from tests import jenkins


@pytest.mark.asyncio
async def test_get_views():
    views = await jenkins.views.get_all()
    assert len(views) == 1
    assert 'all' in map(lambda s: s.lower(), views)


@pytest.mark.asyncio
async def test_is_exists():
    version = await jenkins.get_version()

    if version.major < 2:
        assert await jenkins.views.is_exists('All') is True
    else:
        assert await jenkins.views.is_exists('all') is True
