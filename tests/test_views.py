import contextlib

import pytest

from aiojenkins.exceptions import JenkinsError

VIEW_CONFIG_XML = """<?xml version="1.0" encoding="UTF-8"?>
<hudson.model.ListView>
  <name>{name}</name>
  <filterExecutors>false</filterExecutors>
  <filterQueue>false</filterQueue>
  <properties class="hudson.model.View$PropertyList"/>
  <jobNames>
    <comparator class="hudson.util.CaseInsensitiveComparator"/>
  </jobNames>
  <jobFilters/>
  <columns>
    <hudson.views.StatusColumn/>
    <hudson.views.WeatherColumn/>
    <hudson.views.JobColumn/>
    <hudson.views.LastSuccessColumn/>
    <hudson.views.LastFailureColumn/>
    <hudson.views.LastDurationColumn/>
    <hudson.views.BuildButtonColumn/>
  </columns>
  <recurse>false</recurse>
</hudson.model.ListView>
"""


@pytest.mark.asyncio
async def test_get_views(jenkins):
    views = await jenkins.views.get_all()
    assert len(views) > 0
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


@pytest.mark.asyncio
async def test_view_create_delete(jenkins):
    await jenkins.views.create('test', VIEW_CONFIG_XML.format(name='test'))

    with pytest.raises(JenkinsError):
        await jenkins.views.create('test', VIEW_CONFIG_XML.format(name='test'))

    views = await jenkins.views.get_all()
    assert 'test' in views

    await jenkins.views.delete('test')
    views = await jenkins.views.get_all()
    assert 'test' not in views


@pytest.mark.asyncio
async def test_view_reconfigure(jenkins):
    with contextlib.suppress(JenkinsError):
        await jenkins.views.delete('test2')

    await jenkins.views.create('test2', VIEW_CONFIG_XML.format(name='test2'))

    views = await jenkins.views.get_all()
    assert 'test2' in views

    config = VIEW_CONFIG_XML.format(name='test2')
    config = config.replace(
        '<filterExecutors>false</filterExecutors>',
        '<filterExecutors>true</filterExecutors>'
    )

    await jenkins.views.reconfigure('test2', config)

    config = await jenkins.views.get_config('test2')
    assert '<filterExecutors>true</filterExecutors>' in config
