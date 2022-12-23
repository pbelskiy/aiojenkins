import json
import xml.etree.ElementTree

from typing import Any, Dict, List

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

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    @staticmethod
    def _normalize_name(name: str) -> str:
        # embedded node `master` actually have brackets in HTTP requests
        if name in ('master', 'Built-In Node'):
            return '(master)'
        return name

    async def get_all(self) -> Dict[str, dict]:
        """
        Get available nodes on server.

        Returns:
            Dict[str, dict]: node name, and it`s detailed information.

            Example:

            .. code-block:: python

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
        """
        Get node detailed information.

        Args:
            name (str):
                Node name.

        Returns:
            dict: detailed node information.
        """
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            f'/computer/{name}/api/json',
        )

        info = await response.json()

        info['_disconnected'] = (
            info['offline'] is True and
            info['temporarilyOffline'] is False
        )

        return info

    async def get_failed_builds(self, name: str) -> List[dict]:
        """
        Return list of detalizied failed builds for node name. Actually it
        parsed from RSS feed. usefull for build restart. Ascending builds sort.

        Args:
            name (str):
                Node name.

        Returns:
            List[dict]: builds and their information.

            Example:

            .. code-block:: python

                [{
                  'job_name': 'test',
                  'number': 1,
                  'url': 'http://localhost:8080/job/test/1/'
                }]

        """
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            f'/computer/{name}/rssFailed',
        )

        return _parse_rss(await response.text())

    async def get_all_builds(self, name: str) -> List[dict]:
        """
        Return list of all detalizied builds for node name, actually it parsed
        from RSS feed. Ascending builds sort.

        Args:
            name (str):
                Node name.

        Returns:
            List[dict]: list of all builds for specified node.

            Example:

            .. code-block:: python

                [{
                  'job_name': 'test',
                  'number': 1,
                  'url': 'http://localhost:8080/job/test/1/'
                }]

        """
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            f'/computer/{name}/rssAll',
        )
        return _parse_rss(await response.text())

    async def get_config(self, name: str) -> str:
        """
        Return node config in XML format.

        Args:
            name (str):
                Node name.

        Returns:
            str: node config.
        """
        name = self._normalize_name(name)
        response = await self.jenkins._request(
            'GET',
            f'/computer/{name}/config.xml'
        )

        return await response.text()

    async def is_exists(self, name: str) -> bool:
        """
        Check is node exist.

        Args:
            name (str):
                Node name.

        Returns:
            bool: node existing.
        """
        if name == '':
            return False

        try:
            await self.get_info(name)
        except JenkinsNotFoundError:
            return False
        return True

    @staticmethod
    def construct(**kwargs: Any) -> dict:
        """
        Construct XML node config.

        Returns:
            dict: node XML config.
        """
        return construct_node_config(**kwargs)

    async def create(self, name: str, config: dict) -> None:
        """
        Create new node.

        Args:
            name (str):
                Node name.

            config (str):
                XML config for new node.

        Returns:
            None
        """
        if name in await self.get_all():
            raise JenkinsError(f'Node `{name}` is already exists')

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
        """
        Reconfigure node.

        Args:
            name (str):
                Node name.

            config (str):
                New XML config for node.

        Returns:
            None
        """
        name = self._normalize_name(name)

        if name == '(master)':
            raise JenkinsError('Cannot reconfigure master node')

        await self.jenkins._request(
            'POST',
            f'/computer/{name}/config.xml',
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    async def delete(self, name: str) -> None:
        """
        Delete node.

        Args:
            name (str):
                Node name.

        Returns:
            None
        """
        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/doDelete'
        )

    async def enable(self, name: str) -> None:
        """
        Enable node if disabled.

        Args:
            name (str):
                Node name.

        Returns:
            None
        """
        info = await self.get_info(name)
        if info['temporarilyOffline'] is False:
            return

        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/toggleOffline'
        )

    async def disable(self, name: str, message: str = '') -> None:
        """
        Disable node if enabled.

        Args:
            name (str):
                Node name.

            message (str):
                Reason message.

        Returns:
            None
        """
        info = await self.get_info(name)
        if info['temporarilyOffline'] is True:
            return

        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/toggleOffline',
            params={'offlineMessage': message}
        )

    async def update_offline_reason(self, name: str, message: str) -> None:
        """
        Update reason message of disabled node.

        Args:
            name (str):
                Node name.

            message (str):
                Reason message.

        Returns:
            None
        """
        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/changeOfflineCause',
            params={'offlineMessage': message}
        )

    async def launch_agent(self, name: str) -> None:
        """
        Launch agent on node, for example in case when disconnected.

        State of connection can be determinated by `get_info(...)` method, which
        contains custom property defined by packages: `_disconnected`.

        Args:
            name (str):
                Node name.

        Returns:
            None
        """
        name = self._normalize_name(name)

        await self.jenkins._request(
            'POST',
            f'/computer/{name}/launchSlaveAgent'
        )
