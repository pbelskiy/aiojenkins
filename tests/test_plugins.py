import pytest


@pytest.mark.asyncio
async def test_get_all_plugins(jenkins):
    plugins = await jenkins.plugins.get_all()
    assert len(plugins) >= 0
