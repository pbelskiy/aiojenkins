import json

from typing import Any, Optional, Tuple, Union

from .exceptions import JenkinsNotFoundError
from .utils import parse_build_url


class Builds:
    """
    List of Jenkins tags which can be used insted of build_id number.

    - lastBuild
    - lastCompletedBuild
    - lastFailedBuild
    - lastStableBuild
    - lastSuccessfulBuild
    - lastUnstableBuild
    - lastUnsuccessfulBuild
    """
    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    @staticmethod
    def parse_url(build_url: str) -> Tuple[str, int]:
        """
        Extract job name and build number from url.

        Args:
            build_url (str):
                Build url.

        Returns:
            Tuple[str, int]: job name and build id.
        """
        return parse_build_url(build_url)

    async def get_all(self, name: str) -> list:
        """
        Get list of builds for specified job.

        Example

            .. code-block:: python

                builds = [
                  {'number': 1, 'url': 'http://localhost/job/test/1/'},
                  {'number': 2, 'url': 'http://localhost/job/test/2/'}
                ]

        Args:
            name (str):
                Job name or path (if in folder).

        Returns:
            List: list of build for specified job.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        response = await self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/api/json?tree=allBuilds[number,url]'
        )

        return (await response.json())['allBuilds']

    async def get_info(self, name: str, build_id: Union[int, str]) -> dict:
        """
        Get detailed information about specified build number of job.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            Dict: information about build.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        response = await self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/{build_id}/api/json',
        )

        return await response.json()

    async def get_url_info(self, build_url: str) -> dict:
        """
        Extract job name and build number from url and return info about build.

        Args:
            build_url (str):
                Job name or path (if in folder).

        Returns:
            Dict: information about build.
        """
        job_name, build_id = self.parse_url(build_url)
        return await self.get_info(job_name, build_id)

    async def get_output(self, name: str, build_id: Union[int, str]) -> str:
        """
        Get console output of specified build.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            str: build output.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        response = await self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/{build_id}/consoleText'
        )

        return await response.text()

    async def is_exists(self, name: str, build_id: Union[int, str]) -> bool:
        """
        Check if specified build id of job exists.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            bool: exists or not.
        """
        try:
            await self.get_info(name, build_id)
        except JenkinsNotFoundError:
            return False
        else:
            return True

    async def get_queue_id_info(self, queue_id: int) -> dict:
        response = await self.jenkins._request(
            'GET',
            f'/queue/item/{queue_id}/api/json'
        )

        return await response.json()

    async def start(self,
                    name: str,
                    parameters: Optional[dict] = None,
                    delay: int = 0,
                    **kwargs: Any
                    ) -> Optional[int]:
        """
        Enqueue new build with delay (default is 0 seconds, means immediately)

        Note about delay (quiet-period):
        https://www.jenkins.io/blog/2010/08/11/quiet-period-feature/

        Args:
            name (str):
                Job name or path (if in folder).

            parameters (Optional[Any]):
                Parameters of triggering build as dict or argument, also
                parameters can be passed as kwargs.

                Examples:

                .. code-block:: python

                    start(..., parameters=dict(a=1, b='string'))
                    start(..., a=1, b='string')
                    start(..., parameters=1)
                    start(..., parameters(a=1, b='string'), c=3)

            delay (int):
                Delay before start, default is 0, no delay.

        Returns:
            Optional[int]: queue item id.
        """
        def format_data(parameters: Optional[dict], kwargs: Any) -> Optional[dict]:
            if not (parameters or kwargs):
                return None

            # backward compatibility
            if isinstance(parameters, dict):
                parameters.update(**kwargs)
            elif parameters is None:
                parameters = kwargs
            else:
                parameters = dict(parameters=parameters)
                parameters.update(**kwargs)

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

            return data

        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)
        path = f'/{folder_name}/job/{job_name}'

        data = format_data(parameters, kwargs)
        if data:
            path += '/buildWithParameters'
        else:
            path += '/build'

        response = await self.jenkins._request(
            'POST',
            path,
            params={'delay': delay},
            data=data,
        )

        try:
            # no queue id returned on Jenkins 1.554
            queue_item_url = response.headers['location']
            queue_id = queue_item_url.rstrip('/').split('/')[-1]
            return int(queue_id)
        except (KeyError, ValueError):
            return None

    async def stop(self, name: str, build_id: Union[int, str]) -> None:
        """
        Stop specified build.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        await self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/{build_id}/stop'
        )

    async def delete(self, name: str, build_id: Union[int, str]) -> None:
        """
        Delete specified build.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        await self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/{build_id}/doDelete'
        )
