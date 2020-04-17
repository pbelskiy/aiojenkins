import aiohttp

from urllib.parse import urlencode, urljoin


class JenkinsError(Exception):
    ...


class JenkinsNotFoundError(JenkinsError):
    ...


class Jenkins:

    def __init__(self, host, login=None, password=None):
        self.host = host
        self.auth = None

        if login and password:
            self.auth = aiohttp.BasicAuth(login, password)

    async def _request(self, method: str, path: str, **kwargs):
        if self.auth and not kwargs.get('auth'):
            kwargs['auth'] = self.auth

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.request(
                    method,
                    urljoin(self.host, path),
                    **kwargs,
                )
        except aiohttp.ClientError as e:
            raise JenkinsError from e

        if response.status == 404:
            raise JenkinsNotFoundError

        return response

    async def build_job(self, name: str, parameters: dict=None) -> None:
        data = urlencode(parameters)
        await self._request('POST', f'/job/{name}/buildWithParameters?{data}')

    async def stop_job(self, name: str, build_id: int) -> None:
        await self._request('POST', f'/job/{name}/{build_id}/stop')

    async def get_job_info(self, name: str) -> dict:
        response = await self._request('GET', f'/job/{name}/api/json')
        return await response.json()

    async def get_build_info(self, name: str, build_id: int) -> dict:
        response = await self._request('GET', f'/job/{name}/{build_id}/api/json')
        return await response.json()

    async def get_status(self) -> dict:
        response = await self._request('GET', '/api/json')
        return await response.json()

    async def get_nodes(self) -> dict:
        response = await self._request('GET', '/computer/api/json')
        response = await response.json()
        return {v['displayName']: v for v in response['computer']}
