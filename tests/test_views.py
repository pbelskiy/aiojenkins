import pytest

from tests import jenkins


@pytest.mark.asyncio
async def test_get_views():
    views = await jenkins.views.get_all()
    assert len(views) == 1
    assert 'all' in map(lambda s: s.lower(), views)


@pytest.mark.asyncio
async def test_is_exists():
    assert (await jenkins.views.is_exists('All') or  # <= 1.554
            await jenkins.views.is_exists('all')) is True
