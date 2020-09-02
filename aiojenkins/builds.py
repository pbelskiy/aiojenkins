import json

from typing import Any, Optional, Tuple

from aiojenkins.exceptions import JenkinsNotFoundError
from aiojenkins.utils import parse_build_url


class Builds:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    @staticmethod
    def parse_url(build_url: str) -> Tuple[str, int]:
        """
        Extract job name and build number from build url
        """
        return parse_build_url(build_url)

    async def get_all(self, name: str) -> list:
        """
        Get list of builds for specified job name. Returned example:

        builds = [
          {'number': 1, 'url': 'http://localhost/job/test/1/'},
          {'number': 2, 'url': 'http://localhost/job/test/2/'}
        ]
        """
        response = await self.jenkins._request(
            'GET',
            '/job/{}/api/json?tree=allBuilds[number,url]'.format(name)
        )

        return (await response.json())['allBuilds']

    async def get_info(self, name: str, build_id: int) -> dict:
        """
        Get detailed information about specified build of job
        """
        response = await self.jenkins._request(
            'GET',
            '/job/{}/{}/api/json'.format(name, build_id)
        )

        return await response.json()

    async def get_url_info(self, build_url: str) -> dict:
        """
        Extract job name and build number from url and return info
        """
        job_name, build_id = self.parse_url(build_url)
        return await self.get_info(job_name, build_id)

    async def get_output(self, name: str, build_id: int) -> str:
        """
        Get console output of specified build
        """
        response = await self.jenkins._request(
            'GET',
            '/job/{}/{}/consoleText'.format(name, build_id)
        )

        return await response.text()

    async def is_exists(self, name: str, build_id: int) -> bool:
        try:
            await self.get_info(name, build_id)
        except JenkinsNotFoundError:
            return False
        else:
            return True

    async def get_queue_id_info(self, queue_id: int) -> dict:
        response = await self.jenkins._request(
            'GET',
            '/queue/item/{}/api/json'.format(queue_id)
        )

        return await response.json()

    async def start(self,
                    name: str,
                    parameters: Optional[dict] = None,
                    delay: int = 0
                    ) -> Optional[int]:
        """
        Enqueue new build with delay (default is 0 seconds, means immediately)

        Note about delay (quiet-period):
        https://www.jenkins.io/blog/2010/08/11/quiet-period-feature/
        """
        data = None

        if parameters:
            path = '/job/{}/buildWithParameters'.format(name)

            formatted_parameters = [
                {'name': k, 'value': str(v)} for k, v in parameters.items()
            ]  # type: Any

            if len(formatted_parameters) == 1:
                formatted_parameters = formatted_parameters[0]

            data = {
                'json': json.dumps({
                    'parameter': formatted_parameters,
                    'statusCode': '303',
                    'redirectTo': '.',
                }),
                **parameters,
            }
        else:
            path = '/job/{}/build'.format(name)

        response = await self.jenkins._request(
            'POST',
            path,
            params={'delay': delay},
            data=data,
        )

        # FIXME: on Jenkins 1.554 there is problem, no queue id returned
        queue_item_url = response.headers['location']
        try:
            queue_id = queue_item_url.rstrip('/').split('/')[-1]
            return int(queue_id)
        except ValueError:
            return None

    async def stop(self, name: str, build_id: int) -> None:
        await self.jenkins._request(
            'POST',
            '/job/{}/{}/stop'.format(name, build_id)
        )

    async def delete(self, name: str, build_id: int) -> None:
        await self.jenkins._request(
            'POST',
            '/job/{}/{}/doDelete'.format(name, build_id)
        )
