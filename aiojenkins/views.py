from .exceptions import JenkinsError


class Views:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def get_all(self) -> dict:
        """
        Returns dict of all views and their properties.
        """
        status = await self.jenkins.get_status()
        return {v['name']: v for v in status['views']}

    async def is_exists(self, name: str) -> bool:
        """
        Check if view exists
        """
        views = await self.get_all()
        return name in views

    async def get_config(self, name: str) -> str:
        """
        Return view config in XML format
        """
        response = await self.jenkins._request(
            'GET',
            '/view/{}/config.xml'.format(name)
        )

        return await response.text()

    async def create(self, name: str, config: str) -> None:
        """
        Create view
        """
        if name in await self.get_all():
            raise JenkinsError('View `{}` is already exists'.format(name))

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
        Reconfigure view
        """
        await self.jenkins._request(
            'POST',
            '/view/{}/config.xml'.format(name),
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    async def delete(self, name: str) -> None:
        """
        Delete view
        """
        await self.jenkins._request('POST', '/view/{}/doDelete'.format(name))
