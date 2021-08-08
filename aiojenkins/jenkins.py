import asyncio

from http import HTTPStatus
from typing import Any, NamedTuple, Optional, Tuple, Union

from aiohttp import (
    BasicAuth,
    ClientError,
    ClientResponse,
    ClientSession,
    ClientTimeout,
)

from .builds import Builds
from .exceptions import JenkinsError, JenkinsNotFoundError
from .jobs import Jobs
from .nodes import Nodes
from .plugins import Plugins
from .views import Views

JenkinsVersion = NamedTuple(
    'JenkinsVersion', [('major', int), ('minor', int), ('patch', int)]
)


class RetryClientSession:

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop], options: dict):
        self._validate_retry_argument(options)

        self.total = options['total']
        self.factor = options.get('factor', 1)
        self.statuses = options.get('statuses', [])

        self.session = ClientSession(loop=loop)

    @staticmethod
    def _validate_retry_argument(retry: dict) -> None:
        for key in retry:
            if key not in ('total', 'factor', 'statuses'):
                raise JenkinsError('Unknown key in retry argument: ' + key)

        if retry.get('total', 0) <= 0:
            raise JenkinsError('Invalid `total` in retry argument must be > 0')

    async def request(self, *args: Any, **kwargs: Any) -> ClientResponse:
        for total in range(self.total):
            try:
                response = await self.session.request(*args, **kwargs)
            except (ClientError, asyncio.TimeoutError) as e:
                if total + 1 == self.total:
                    raise JenkinsError from e
            else:
                if response.status not in self.statuses:
                    break

            await asyncio.sleep(self.factor * (2 ** (total - 1)))

        return response

    async def close(self) -> None:
        await self.session.close()


class Jenkins:

    _session = None

    def __init__(self,
                 host: str,
                 login: Optional[str] = None,
                 password: Optional[str] = None,
                 *,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 verify: bool = True,
                 timeout: Optional[float] = None,
                 retry: Optional[dict] = None):
        """
        Core library class.

        Args:
            host (str):
                URL of jenkins server.

            login (Optional[str]):
                Login, user name.

            password (Optional[str]):
                Password for login.

            loop (Optional[AbstractEventLoop]):
                Asyncio current event loop.

            verify (Optional[bool]):
                Verify SSL (default: true).

            timeout (Optional[int]):
                HTTP request timeout.

            retry (Optional[dict]):
                Retry options to prevent failures if server restarting or
                temporary network problem. Disabled by default use total > 0
                to enable.

                - total: ``int`` Total retries count.
                - factor: ``int`` Sleep between retries (default 1)
                    {factor} * (2 ** ({number of total retries} - 1))
                - statuses: ``List[int]`` HTTP statues retries on. (default [])

                Example:
                .. code-block:: python
                    retry = dict(
                        total=10,
                        factor=1,
                        statuses=[500]
                    )
        Returns:
            Jenkins instance
        """
        self.host = host.rstrip('/')
        self.loop = loop or asyncio.get_event_loop()
        self.verify = verify
        self.retry = retry

        self.auth = None  # type: Any
        self.timeout = None  # type: Any
        self.crumb = None  # type: Any

        if login and password:
            self.auth = BasicAuth(login, password)

        if timeout:
            self.timeout = ClientTimeout(total=timeout)

        self.builds = Builds(self)
        self.jobs = Jobs(self)
        self.nodes = Nodes(self)
        self.plugins = Plugins(self)
        self.views = Views(self)

    async def _get_session(self):
        if self._session:
            return self._session

        if self.retry:
            self._session = RetryClientSession(self.loop, self.retry)
        else:
            self._session = ClientSession(loop=self.loop)

        return self._session

    async def _http_request(self,
                            method: str,
                            path: str,
                            **kwargs: Any) -> ClientResponse:
        if self.auth and 'auth' not in kwargs:
            kwargs['auth'] = self.auth

        if self.timeout and 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        if self.crumb:
            kwargs.setdefault('headers', {})
            kwargs['headers'].update(self.crumb)

        session = await self._get_session()
        try:
            if path.startswith('http'):
                url = path
            else:
                url = self.host + path

            response = await session.request(
                method,
                url,
                allow_redirects=False,
                ssl=self.verify,
                **kwargs,
            )
        except ClientError as e:
            raise JenkinsError from e

        if response.status == HTTPStatus.NOT_FOUND:
            raise JenkinsNotFoundError

        if response.status >= HTTPStatus.BAD_REQUEST:
            text = await response.text()

            if response.status in (
                    HTTPStatus.UNAUTHORIZED,
                    HTTPStatus.FORBIDDEN,
                    HTTPStatus.INTERNAL_SERVER_ERROR):
                details = 'probably authentication problem:\n' + text
            else:
                details = '\n' + text

            raise JenkinsError(
                'Request error [{}], {}'.format(response.status, details),
                status=response.status,
            )

        return response

    async def _get_crumb(self) -> Union[bool, dict]:
        try:
            response = await self._http_request('GET', '/crumbIssuer/api/json')
        except JenkinsNotFoundError:
            return False

        content = await response.json()
        self.crumb = {content['crumbRequestField']: content['crumb']}
        return self.crumb

    async def _request(self,
                       method: str,
                       path: str,
                       **kwargs: Any) -> ClientResponse:
        """
        Core class method for endpoints, which wraps auto crumb detection
        """
        if self.crumb:
            try:
                return await self._http_request(method, path, **kwargs)
            except JenkinsError as e:
                if e.status != HTTPStatus.FORBIDDEN:
                    raise

        if self.crumb is not False:
            self.crumb = await self._get_crumb()

        return await self._http_request(method, path, **kwargs)

    @staticmethod
    def _get_folder_and_job_name(name: str) -> Tuple[str, str]:
        parts = name.split('/')

        job_name = parts[-1]
        folder_name = ''

        for folder in parts[:-1]:
            folder_name += 'job/{}/'.format(folder)

        return folder_name, job_name

    async def close(self) -> None:
        """
        Finalize client, close http session.

        Returns:
            None
        """
        if self._session:
            await self._session.close()

    async def get_status(self) -> dict:
        """
        Get server status.

        Returns:
            dict: jenkins server details.
        """
        response = await self._request('GET', '/api/json')
        return await response.json()

    async def get_version(self) -> JenkinsVersion:
        """
        Get server version.

        Returns:
            JenkinsVersion: named tuple with minor, major, patch version.
        """
        response = await self._request('GET', '/')
        header = response.headers.get('X-Jenkins')
        if not header:
            raise JenkinsError('Header `X-Jenkins` isn`t found in response')

        return JenkinsVersion(*map(int, header.split('.')))

    async def is_ready(self) -> bool:
        """
        Determines is server loaded and ready for work.

        Returns:
            bool: ready state.
        """
        try:
            status = await self.get_status()
            return ('mode' in status)
        except JenkinsError:
            return False

    async def wait_until_ready(self, sleep_interval_sec: float = 1.0) -> None:
        """
        Blocks until server is completely loaded.

        Args:
            sleep_interval_sec (float): delay between checks.

        Returns:
            None
        """
        while (await self.is_ready()) is False:
            await asyncio.sleep(sleep_interval_sec)

    async def quiet_down(self) -> None:
        """
        Start server quiet down period, new builds will not be started.

        Returns:
            None
        """
        await self._request('POST', '/quietDown')

    async def cancel_quiet_down(self) -> None:
        """
        Cancel server quiet down period.

        Returns:
            None
        """
        await self._request('POST', '/cancelQuietDown')

    async def restart(self) -> None:
        """
        Restart server immediately.

        Returns:
            None
        """
        await self._request('POST', '/restart')

    async def safe_restart(self) -> None:
        """
        Restart server when installation is complete and no jobs are running.

        Returns:
            None
        """
        await self._request('POST', '/safeRestart')

    @staticmethod
    def _build_token_url(do: str) -> str:
        return '/me/descriptorByName/jenkins.security.ApiTokenProperty/' + do

    async def generate_token(self, name: str) -> Tuple[str, str]:
        """
        Generate new API token.

        Args:
            name (str): name of token.

        Returns:
            Tuple[str, str]: tokenValue - uses for authorization,
                             tokenUuid - uses for revoke
        """
        params = {'newTokenName': name}

        response = await self._request(
            'POST',
            self._build_token_url('generateNewToken'),
            params=params
        )

        content = await response.json()
        if content['status'] != 'ok':
            raise JenkinsError('Non OK status returned: ' + str(content))

        return content['data']['tokenValue'], content['data']['tokenUuid']

    async def revoke_token(self, token_uuid: str) -> None:
        """
        Revoke API token, please note that uuid is used, not value.

        Args:
            token_uuid (str): uuid of token to be revoked.

        Returns:
            None
        """
        params = {'tokenUuid': token_uuid}

        await self._request(
            'POST',
            self._build_token_url('revoke'),
            params=params
        )

    async def run_groovy_script(self, script: str) -> str:
        """
        Execute Groovy script on the server.

        Args:
            script (str): script content.

        Returns:
            str: output of script.
        """
        response = await self._request(
            'POST',
            '/scriptText',
            data={'script': script}
        )

        return await response.text()
