import json

from urllib.parse import urljoin

import aiohttp


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

    async def _http_request(self, method: str, path: str, **kwargs):
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

        if response.status in (401, 403, 500):
            text = await response.text()
            raise JenkinsError(
                f'Request error [{response.status}], ' +
                f'probably authentication problem:\n{text}'
            )

        return response

    async def _get_crumb(self) -> dict:
        if self.crumb is False:
            return None

        if self.crumb:
            return self.crumb

        try:
            response = await self._http_request('GET', '/crumbIssuer/api/json')
        except JenkinsNotFoundError:
            self.crumb = False
            return None

        data = await response.json()
        self.crumb = {data['crumbRequestField']: data['crumb']}
        return self.crumb

    async def _request(self, method: str, path: str, **kwargs):
        kwargs.setdefault('headers', {})
        crumb = await self._get_crumb()
        if crumb:
            kwargs['headers'].update(crumb)

        return await self._http_request(method, path, **kwargs)

    @staticmethod
    def _normalize_node_name(name: str) -> str:
        # embedded node `master` actually have brackets in HTTP requests
        if name == 'master':
            return '(master)'
        return name

    async def create_job(self, name: str, config: str) -> None:
        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}
        await self._request('POST', '/createItem',
            params=params,
            data=config,
            headers=headers
        )

    async def build_job(self, name: str, parameters: dict=None) -> None:
        await self._request('POST',
            f'/job/{name}/buildWithParameters',
            params=parameters,
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

    async def get_nodes(self) -> dict:
        response = await self._request('GET', '/computer/api/json')
        response = await response.json()
        return {v['displayName']: v for v in response['computer']}

    async def get_node_info(self, name: str) -> dict:
        name = self._normalize_node_name(name)
        response = await self._request('GET', f'/computer/{name}/api/json')
        return await response.json()

    async def is_node_exists(self, name: str) -> bool:
        if name == '':
            return False

        try:
            await self.get_node_info(name)
        except JenkinsNotFoundError:
            return False
        return True

    async def disable_node(self, name: str, message: str='') -> None:
        info = await self.get_node_info(name)
        if info['offline']:
            return

        name = self._normalize_node_name(name)
        params = {'offlineMessage': message}
        await self._request('POST', f'/computer/{name}/toggleOffline',
            params=params
        )

    async def enable_node(self, name: str) -> None:
        info = await self.get_node_info(name)
        if not info['offline']:
            return

        name = self._normalize_node_name(name)
        await self._request('POST', f'/computer/{name}/toggleOffline')

    async def update_node_offline_reason(self, name: str, message: str) -> None:
        name = self._normalize_node_name(name)
        await self._request('POST', f'/computer/{name}/changeOfflineCause',
            params={'offlineMessage': message}
        )

    async def create_node(self, name: str, config: dict) -> None:
        if name in await self.get_nodes():
            raise JenkinsError(f'Node `{name}` is already exists')

        if 'type' not in config:
            config['type'] = 'hudson.slaves.DumbSlave'

        config['name'] = name

        params = {
            'name': name,
            'type': config['type'],
            'json': json.dumps(config)
        }
        await self._request('POST', '/computer/doCreateItem', params=params)

    async def delete_node(self, name: str) -> None:
        name = self._normalize_node_name(name)
        await self._request('POST', f'/computer/{name}/doDelete')
