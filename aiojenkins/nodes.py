import json
import xml.etree.ElementTree

from typing import Any, List

from .exceptions import JenkinsError, JenkinsNotFoundError
from .utils import construct_node_config, parse_build_url


def _parse_rss(rss: str) -> list:
    builds = []
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    root = xml.etree.ElementTree.fromstring(rss)
    for entry in root.findall('atom:entry', ns):
        link = entry.find('atom:link', ns)
        if link is not None:
            build_url = link.attrib['href']
            job_name, build_id = parse_build_url(build_url)

            builds.append({
                'url': build_url,
                'job_name': job_name,
                'number': build_id,
            })

    return list(reversed(builds))


class Nodes:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    @staticmethod
    def _normalize_name(name: str) -> str:
        # embedded node `master` actually have brackets in HTTP requests
        if name == 'master':
            return '(master)'
        return name

    async def get_all(self) -> dict:
        """
        Get available nodes on server. Example dict result:
        {
            "master": dict(...),
            "buildbot1": dict(...)
        }
        """
        response = await self.jenkins._request(
            'GET',
            '/computer/api/json'
        )

        nodes = await response.json()
        return {v['displayName']: v for v in nodes['computer']}

    async def get_info(self, name: str) -> dict:
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            '/computer/{}/api/json'.format(name),
        )
        return await response.json()

    async def get_failed_builds(self, name: str) -> List[dict]:
        """
        Return list of detalizied failed builds for node name, actually it
        parsed from RSS feed. usefull for build restart. Ascending builds sort.

        Example: [{
          'job_name': 'test',
          'number': 1,
          'url': 'http://localhost:8080/job/test/1/'
        }]
        """
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            '/computer/{}/rssFailed'.format(name),
        )
        return _parse_rss(await response.text())

    async def get_all_builds(self, name: str) -> List[dict]:
        """
        Return list of all detalizied builds for node name, actually it parsed
        from RSS feed. Ascending builds sort.

        Example: [{
          'job_name': 'test',
          'number': 1,
          'url': 'http://localhost:8080/job/test/1/'
        }]
        """
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            '/computer/{}/rssAll'.format(name),
        )
        return _parse_rss(await response.text())

    async def get_config(self, name: str) -> str:
        """
        Return node config in XML format
        """
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            '/computer/{}/config.xml'.format(name)
        )

        return await response.text()

    async def is_exists(self, name: str) -> bool:
        if name == '':
            return False

        try:
            await self.get_info(name)
        except JenkinsNotFoundError:
            return False
        return True

    def construct(self, **kwargs: Any):
        """
        Jenkins node constructor, returns dict to be passed to create method.
        """
        return construct_node_config(**kwargs)

    async def create(self, name: str, config: dict) -> None:
        if name in await self.get_all():
            raise JenkinsError('Node `{}` is already exists'.format(name))

        if 'type' not in config:
            config['type'] = 'hudson.slaves.DumbSlave'

        config['name'] = name

        params = {
            'name': name,
            'type': config['type'],
            'json': json.dumps(config)
        }

        await self.jenkins._request(
            'POST',
            '/computer/doCreateItem',
            params=params,
        )

    async def reconfigure(self, name: str, config: str) -> None:
        name = self._normalize_name(name)

        if name == '(master)':
            raise JenkinsError('Cannot reconfigure master node')

        await self.jenkins._request(
            'POST',
            '/computer/{}/config.xml'.format(name),
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    async def delete(self, name: str) -> None:
        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            '/computer/{}/doDelete'.format(name)
        )

    async def enable(self, name: str) -> None:
        info = await self.get_info(name)
        if not info['offline']:
            return

        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            '/computer/{}/toggleOffline'.format(name)
        )

    async def disable(self, name: str, message: str = '') -> None:
        info = await self.get_info(name)
        if info['offline']:
            return

        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            '/computer/{}/toggleOffline'.format(name),
            params={'offlineMessage': message}
        )

    async def update_offline_reason(self, name: str, message: str) -> None:
        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            '/computer/{}/changeOfflineCause'.format(name),
            params={'offlineMessage': message}
        )
