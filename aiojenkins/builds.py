import json

from typing import Any


class Builds:

    def __init__(self, jenkins):
        self.jenkins = jenkins

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
            f'/job/{name}/api/json?tree=allBuilds[number,url]'
        )

        return (await response.json())['allBuilds']

    async def get_info(self, name: str, build_id: int) -> dict:
        """
        Get detailed information about specified build of job
        """
        response = await self.jenkins._request(
            'GET',
            f'/job/{name}/{build_id}/api/json'
        )

        return await response.json()

    async def get_output(self, name: str, build_id: int) -> str:
        """
        Get console output of specified build
        """
        response = await self.jenkins._request(
            'GET',
            f'/job/{name}/{build_id}/consoleText'
        )

        return await response.text()

    async def start(self,
                    name: str,
                    parameters: dict = None,
                    delay: int = 0
                    ) -> None:
        """
        Enqueue new build with delay (default is 0 seconds, means immediately)

        Note about delay (quiet-period):
        https://www.jenkins.io/blog/2010/08/11/quiet-period-feature/
        """
        data = None
        if parameters:
            formatted_parameters: Any = [
                {'name': k, 'value': str(v)} for k, v in parameters.items()
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

        params = {'delay': delay}

        await self.jenkins._request(
            'POST',
            f'/job/{name}/build',
            params=params,
            data=data,
        )

    async def stop(self, name: str, build_id: int) -> None:
        await self.jenkins._request(
            'POST',
            f'/job/{name}/{build_id}/stop'
        )

    async def delete(self, name: str, build_id: int) -> None:
        await self.jenkins._request(
            'POST',
            f'/job/{name}/{build_id}/doDelete'
        )
