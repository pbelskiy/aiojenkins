class Jobs:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def create(self, name: str, config: str) -> None:
        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}

        await self.jenkins._request(
            'POST', '/createItem',
            params=params,
            data=config,
            headers=headers
        )

    async def delete(self, name: str) -> None:
        await self.jenkins._request('POST', f'/job/{name}/doDelete')

    async def enable(self, name: str) -> None:
        await self.jenkins._request('POST', f'/job/{name}/enable')

    async def disable(self, name: str) -> None:
        await self.jenkins._request('POST', f'/job/{name}/disable')

    async def get_config(self, name: str) -> str:
        response = await self.jenkins._request('GET', f'/job/{name}/config.xml')
        return await response.text()

    async def get_info(self, name: str) -> dict:
        response = await self.jenkins._request('GET', f'/job/{name}/api/json')
        return await response.json()
