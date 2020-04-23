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
        self.crumb = None

        if login and password:
            self.auth = aiohttp.BasicAuth(login, password)

    async def _get_crumb(self) -> dict:
        if self.crumb is False:
            return None

        if self.crumb:
            return self.crumb

        async with aiohttp.ClientSession() as session:
            response = await session.get(
                urljoin(self.host, 'crumbIssuer/api/json'),
                auth=self.auth
            )

        if response.status == 404:
            self.crumb = False
            return None

        data = await response.json()
        self.crumb = {data['crumbRequestField']: data['crumb']}
        return self.crumb

    async def _request(self, method: str, path: str, **kwargs):
        if self.auth and not kwargs.get('auth'):
            kwargs['auth'] = self.auth

        kwargs.setdefault('headers', {})
        crumb = await self._get_crumb()
        if crumb:
            kwargs['headers'].update(crumb)

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

        if response.status in (401, 403, 500):
            raise JenkinsError(
                f'Request error [{response.status}], ' +
                f'probably authentication problem:\n{await response.text()}'
            )

        return response

    async def create_job(self, name: str, config: str) -> None:
        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}
        await self._request('POST', '/createItem',
            params=params,
            data=config,
            headers=headers
        )

    async def get_job_config(self, name: str) -> str:
        response = await self._request('GET', f'/job/{name}/config.xml')
        return await response.text()

    async def delete_job(self, name: str) -> None:
        await self._request('POST', f'/job/{name}/doDelete')

    async def build_job(self, name: str, parameters: dict=None) -> None:
        data = urlencode(parameters)
        await self._request('POST', f'/job/{name}/buildWithParameters?{data}')

    async def stop_build(self, name: str, build_id: int) -> None:
        await self._request('POST', f'/job/{name}/{build_id}/stop')

    async def delete_build(self, name: str, build_id: int) -> None:
        await self._request('POST', f'/job/{name}/{build_id}/doDelete')

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
