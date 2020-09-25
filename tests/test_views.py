import pytest


@pytest.mark.asyncio
async def test_get_views(jenkins):
    views = await jenkins.views.get_all()
    assert len(views) == 1
    assert 'all' in map(lambda s: s.lower(), views)


@pytest.mark.asyncio
async def test_is_exists(jenkins):
    version = await jenkins.get_version()

    if version.major < 2:
        assert await jenkins.views.is_exists('All') is True
    else:
        assert await jenkins.views.is_exists('all') is True


@pytest.mark.asyncio
async def test_get_config(jenkins):
    version = await jenkins.get_version()

    if version.major < 2:
        assert len(await jenkins.views.get_config('All')) > 0
    else:
        assert len(await jenkins.views.get_config('all')) > 0
