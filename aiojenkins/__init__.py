import asyncio
import urllib

from http import HTTPStatus
from typing import Tuple, NamedTuple

import aiohttp

from aiojenkins.exceptions import (
    JenkinsError,
    JenkinsNotFoundError,
)

from aiojenkins.builds import Builds
from aiojenkins.jobs import Jobs
from aiojenkins.nodes import Nodes


class JenkinsVersion(NamedTuple):
    major: int = 0
    minor: int = 0
    patch: int = 0


class Jenkins:

    def __init__(self, host, login=None, password=None):
        self.host = host
        self.auth = None
        self.crumb = None
        self.cookies = None

        if login and password:
            self.auth = aiohttp.BasicAuth(login, password)

        self._nodes = Nodes(self)
        self._jobs = Jobs(self)
        self._builds = Builds(self)

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
                    allow_redirects=False,
                    **kwargs,
                )
        except aiohttp.ClientError as e:
            raise JenkinsError from e

        if response.status == HTTPStatus.NOT_FOUND:
            raise JenkinsNotFoundError

        if response.status >= HTTPStatus.BAD_REQUEST:
            text = await response.text()

            if response.status in (
                    HTTPStatus.UNAUTHORIZED,
                    HTTPStatus.FORBIDDEN,
                    HTTPStatus.INTERNAL_SERVER_ERROR):
                details = f'probably authentication problem:\n{text}'
            else:
                details = f'\n{text}'

            raise JenkinsError(
                f'Request error [{response.status}], {details}',
                status=response.status,
            )

        if response.cookies:
            self.cookies = response.cookies

        return response

    async def _get_crumb(self):
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

    async def get_version(self) -> JenkinsVersion:
        response = await self._request('GET', '/')
        header = response.headers.get('X-Jenkins')
        return JenkinsVersion(*map(int, header.split('.')))

    async def is_ready(self) -> bool:
        """
        Determines is server loaded and ready for work
        """
        try:
            status = await self.get_status()
            return ('mode' in status)
        except JenkinsError:
            return False

    async def wait_until_ready(self, sleep_interval_sec: float = 1.0) -> None:
        """
        Blocks until server is completely loaded
        """
        while (await self.is_ready()) is False:
            await asyncio.sleep(sleep_interval_sec)

    async def quiet_down(self) -> None:
        """
        Start server quiet down period, new builds will not be started
        """
        await self._request('POST', '/quietDown')

    async def cancel_quiet_down(self) -> None:
        """
        Cancel server quiet down period
        """
        await self._request('POST', '/cancelQuietDown')

    async def restart(self) -> None:
        """
        Restart server immediately
        """
        await self._request('POST', '/restart')

    async def safe_restart(self) -> None:
        """
        Restart server when installation is complete and no jobs are running
        """
        await self._request('POST', '/safeRestart')

    @staticmethod
    def _build_token_url(do: str) -> str:
        return f'/me/descriptorByName/jenkins.security.ApiTokenProperty/{do}'

    async def generate_token(self, name: str) -> Tuple[str, str]:
        """
        Generate new API token.

        Returns two values:
        * tokenValue - uses for authorization
        * tokenUuid - uses for revoke
        """
        params = {'newTokenName': name}

        response = await self._request(
            'POST',
            self._build_token_url('generateNewToken'),
            params=params
        )

        response = await response.json()
        if response['status'] != 'ok':
            raise JenkinsError(f'Non OK status returned: `{response}`')

        return response['data']['tokenValue'], response['data']['tokenUuid']

    async def revoke_token(self, token_uuid: str) -> None:
        """
        Revoke API token, please note that uuid is used, not value.
        """
        params = {'tokenUuid': token_uuid}

        await self._request(
            'POST',
            self._build_token_url('revoke'),
            params=params
        )

    @property
    def nodes(self):
        return self._nodes

    @property
    def jobs(self):
        return self._jobs

    @property
    def builds(self):
        return self._builds
