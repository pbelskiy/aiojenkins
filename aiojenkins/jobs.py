from aiojenkins.utils import construct_job_config


class Jobs:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def get_all(self) -> dict:
        """
        Get list of builds for specified job name. Returned example:

        jobs = [
            {'name': 'test', 'url': 'http://localhost/job/test/'},
            {'name': 'test_builds', 'url': 'http://localhost/job/test_builds/'}
        ]
        """
        status = await self.jenkins.get_status()
        return {v['name']: v for v in status['jobs']}

    async def get_info(self, name: str) -> dict:
        response = await self.jenkins._request(
            'GET',
            f'/job/{name}/api/json'
        )

        return await response.json()

    def construct(self, *args, **kwargs) -> str:
        """
        Jenkins job XML constructor
        """
        return construct_job_config(*args, **kwargs)

    async def get_config(self, name: str) -> str:
        response = await self.jenkins._request(
            'GET',
            f'/job/{name}/config.xml'
        )

        return await response.text()

    async def create(self, name: str, config: str) -> None:
        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}

        await self.jenkins._request(
            'POST',
            '/createItem',
            params=params,
            data=config,
            headers=headers
        )

    async def delete(self, name: str) -> None:
        await self.jenkins._request(
            'POST',
            f'/job/{name}/doDelete'
        )

    async def copy(self, name: str, new_name: str) -> None:
        params = {
            'mode': 'copy',
            'from': name,
            'name': new_name,
        }

        await self.jenkins._request(
            'POST',
            '/createItem',
            params=params
        )

    async def rename(self, name: str, new_name: str) -> None:
        params = {'newName': new_name}

        await self.jenkins._request(
            'POST',
            f'/job/{name}/doRename',
            params=params
        )

    async def enable(self, name: str) -> None:
        await self.jenkins._request(
            'POST',
            f'/job/{name}/enable'
        )

    async def disable(self, name: str) -> None:
        await self.jenkins._request(
            'POST',
            f'/job/{name}/disable'
        )
