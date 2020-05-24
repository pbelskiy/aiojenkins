import json

from aiojenkins.exceptions import (
    JenkinsError,
    JenkinsNotFoundError,
)


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
            f'/computer/{name}/api/json',
        )
        return await response.json()

    async def is_exists(self, name: str) -> bool:
        if name == '':
            return False

        try:
            await self.get_info(name)
        except JenkinsNotFoundError:
            return False
        return True

    async def create(self, name: str, config: dict) -> None:
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

    async def delete(self, name: str) -> None:
        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/doDelete'
        )

    async def enable(self, name: str) -> None:
        info = await self.get_info(name)
        if not info['offline']:
            return

        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/toggleOffline'
        )

    async def disable(self, name: str, message: str = '') -> None:
        info = await self.get_info(name)
        if info['offline']:
            return

        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/toggleOffline',
            params={'offlineMessage': message}
        )

    async def update_offline_reason(self, name: str, message: str) -> None:
        name = self._normalize_name(name)
        await self.jenkins._request(
            'POST',
            f'/computer/{name}/changeOfflineCause',
            params={'offlineMessage': message}
        )
