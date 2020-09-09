import pytest

from tests import jenkins


@pytest.mark.asyncio
async def test_get_views():
    views = await jenkins.views.get_all()
    assert len(views) == 1
    assert 'all' in map(lambda s: s.lower(), views)
