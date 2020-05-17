import json
import urllib

import aiohttp

from aiojenkins.exceptions import (
    JenkinsError,
    JenkinsNotFoundError,
)

from aiojenkins.builds import Build
from aiojenkins.jobs import Job
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
        self._jobs = Job(self)
        self._builds = Build(self)

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

    async def get_status(self) -> dict:
        response = await self._request('GET', '/api/json')
        return await response.json()

    @property
    def nodes(self):
        return self._nodes

    @property
    def jobs(self):
        return self._jobs

    @property
    def builds(self):
        return self._builds
