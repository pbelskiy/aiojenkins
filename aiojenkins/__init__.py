import json
import urllib

import aiohttp

from aiojenkins.exceptions import JenkinsError, JenkinsNotFoundError
from aiojenkins.nodes import Node


class Jenkins:

    def __init__(self, host, login=None, password=None):
        self.host = host
        self.auth = None
        self.crumb = None
        self.cookies = None

        if login and password:
            self.auth = aiohttp.BasicAuth(login, password)

        self._nodes = Node(self)

    async def _http_request(self, method: str, path: str, **kwargs):
        if self.auth and not kwargs.get('auth'):
            kwargs['auth'] = self.auth

        if self.crumb:
            kwargs.setdefault('headers', {})
            kwargs['headers'].update(self.crumb)

        try:
            async with aiohttp.ClientSession(cookies=self.cookies) as session:
                response = await session.request(
                    method,
                    urllib.parse.urljoin(self.host, path),
                    **kwargs,
                )
        except aiohttp.ClientError as e:
            raise JenkinsError from e

        if response.status == 404:
            raise JenkinsNotFoundError

        if response.status in (401, 403, 500):
            text = await response.text()
            raise JenkinsError(
                f'Request error [{response.status}], '
                f'probably authentication problem:\n{text}',
                status=response.status,
            )

        if response.cookies:
            self.cookies = response.cookies

        return response

    async def _get_crumb(self) -> dict:
        try:
            response = await self._http_request('GET', '/crumbIssuer/api/json')
        except JenkinsNotFoundError:
            return False

        data = await response.json()
        self.crumb = {data['crumbRequestField']: data['crumb']}
        return self.crumb

    async def _request(self, method: str, path: str, **kwargs):
        if self.crumb:
            try:
                return await self._http_request(method, path, **kwargs)
            except JenkinsError as e:
                if e.status != 403:
                    raise

        if self.crumb is not False:
            self.crumb = await self._get_crumb()

        return await self._http_request(method, path, **kwargs)

    async def create_job(self, name: str, config: str) -> None:
        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}
        await self._request('POST', '/createItem',
            params=params,
            data=config,
            headers=headers
        )

    async def build_job(self, name: str, parameters: dict=None, delay: int=0) -> None:
        """
        Enqueue new build with delay (default is 0 seconds, means immediately)

        Note about delay (quiet-period):
        https://www.jenkins.io/blog/2010/08/11/quiet-period-feature/
        """
        data = None
        if parameters:
            formatted_parameters = [
                {'name': k, 'value': str(v)}
                for k, v in parameters.items()
            ]

            if len(formatted_parameters) == 1:
                formatted_parameters = formatted_parameters[0]

            data = {
                'json': json.dumps({
                    'parameter': formatted_parameters,
                    'statusCode': '303',
                    'redirectTo': '.',
                })
            }

        await self._request('POST',
            f'/job/{name}/build',
            params={'delay': delay},
            data=data,
        )

    async def delete_job(self, name: str) -> None:
        await self._request('POST', f'/job/{name}/doDelete')

    async def enable_job(self, name: str) -> None:
        await self._request('POST', f'/job/{name}/enable')

    async def disable_job(self, name: str) -> None:
        await self._request('POST', f'/job/{name}/disable')

    async def get_job_config(self, name: str) -> str:
        response = await self._request('GET', f'/job/{name}/config.xml')
        return await response.text()

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

    @property
    def nodes(self):
        return self._nodes
