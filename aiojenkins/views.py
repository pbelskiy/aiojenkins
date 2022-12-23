from typing import Dict

from .exceptions import JenkinsError


class Views:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    async def get_all(self) -> Dict[str, dict]:
        """
        Get all views and their details.

        Returns:
            Dict[str, dict] - plugin name and plugin properties.
        """
        status = await self.jenkins.get_status()
        return {v['name']: v for v in status['views']}

    async def is_exists(self, name: str) -> bool:
        """
        Check if view exists.

        Args:
            name (str):
                View name.

        Returns:
            bool: view existing
        """
        views = await self.get_all()
        return name in views

    async def get_config(self, name: str) -> str:
        """
        Return view config in XML format.

        Args:
            name (str):
                View name.

        Returns:
            str: XML config of view.
        """
        response = await self.jenkins._request(
            'GET',
            f'/view/{name}/config.xml'
        )

        return await response.text()

    async def create(self, name: str, config: str) -> None:
        """
        Create view using XML config.

        Args:
            name (str):
                View name.

            config (str):
                XML config.

        Returns:
            None
        """
        if name in await self.get_all():
            raise JenkinsError(f'View `{name}` is already exists')

        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}

        await self.jenkins._request(
            'POST',
            '/createView',
            data=config,
            params=params,
            headers=headers,
        )

    async def reconfigure(self, name: str, config: str) -> None:
        """
        Reconfigure view.

        Args:
            name (str):
                View name.

            config (str):
                XML config.

        Returns:
            None
        """
        await self.jenkins._request(
            'POST',
            f'/view/{name}/config.xml',
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    async def delete(self, name: str) -> None:
        """
        Delete view.

        Args:
            name (str):
                View name.

        Returns:
            None
        """
        await self.jenkins._request('POST', f'/view/{name}/doDelete')
