from typing import Any, Dict

from .exceptions import JenkinsNotFoundError
from .utils import construct_job_config


class Jobs:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def _get_all_jobs(self, url: str, parent: str) -> Dict[str, dict]:
        all_jobs = {}

        response = await self.jenkins._request('GET', url + '/api/json')
        jobs = (await response.json())['jobs']

        for job in jobs:
            all_jobs[parent + job['name']] = job

            if 'Folder' in job.get('_class', ''):
                all_jobs.update(await self._get_all_jobs(
                    job['url'],
                    parent + job['name'] + '/'
                ))

        return all_jobs

    async def get_all(self) -> Dict[str, dict]:
        """
        Get dict of all existed jobs in system, including jobs in folder.

        Returns: Dict[str, dict] - name and job properties.

        Example: {
            'test': {
                'name': 'test',
                'url': 'http://localhost/job/test/'
            },
            'folder/foo': {
                'name': 'folder/job',
                'url': 'http://localhost/job/folder/job/foo/'
            }
        }
        """
        return await self._get_all_jobs('', '')

    async def get_info(self, name: str) -> dict:
        """
        Get detailed information of specified job.

        Args:
            name (str): job name.

        Returns:
            dict: job details.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        response = await self.jenkins._request(
            'GET',
            '/{}/job/{}/api/json'.format(folder_name, job_name)
        )

        return await response.json()

    async def get_config(self, name: str) -> str:
        """
        Get XML config of specified job.

        Args:
            name (str): job name.

        Returns:
            str: XML config
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        response = await self.jenkins._request(
            'GET',
            '/{}/job/{}/config.xml'.format(folder_name, job_name)
        )

        return await response.text()

    async def is_exists(self, name: str) -> bool:
        """
        Check if specified job exists.

        Args:
            name (str): job name.

        Returns:
            bool: job exists or not
        """
        try:
            await self.get_info(name)
        except JenkinsNotFoundError:
            return False
        else:
            return True

    def construct_config(self, **kwargs: Any) -> str:
        """
        Jenkins job XML constructor, cannot be used for folder creating yet.
        """
        return construct_job_config(**kwargs)

    async def create(self, name: str, config: str) -> None:
        """
        Create new jenkins job (project).

        Args:
            name (str): job name.
            config (str): XML config of new job. It`s convenient way to use
              `get_config()` to get existing job config and change it on your
              taste, or to use `construct_config()` method.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        headers = {'Content-Type': 'text/xml'}
        params = {'name': job_name}

        await self.jenkins._request(
            'POST',
            '/{}/createItem'.format(folder_name),
            params=params,
            data=config,
            headers=headers
        )

    async def reconfigure(self, name: str, config: str) -> None:
        """
        Reconfigure specified job name.

        Args:
            name (str): job name or path (within folder).
            config (str): XML config of new job. It`s convenient way to use
              `get_config()` to get existing job config and change it on your
              taste, or to use `construct_config()` method.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        await self.jenkins._request(
            'POST',
            '/{}/job/{}/config.xml'.format(folder_name, job_name),
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    async def delete(self, name: str) -> None:
        """
        Delete existed jenkins job (project).

        Args:
            name (str): job name. For job in folder just use `/`.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        await self.jenkins._request(
            'POST',
            '/{}/job/{}/doDelete'.format(folder_name, job_name)
        )

    async def copy(self, name: str, new_name: str) -> None:
        """
        Copy specified job.

        Args:
            name (str): job name or path (within folder).
            new_name (str): new job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        params = {
            'mode': 'copy',
            'from': job_name,
            'name': new_name,
        }

        await self.jenkins._request(
            'POST',
            '/{}/createItem'.format(folder_name),
            params=params
        )

    async def rename(self, name: str, new_name: str) -> None:
        """
        Rename specified job name.

        Args:
            name (str): job name or path (within folder).
            new_name (str): new job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        params = {
            'newName': new_name
        }

        await self.jenkins._request(
            'POST',
            '/{}/job/{}/doRename'.format(folder_name, job_name),
            params=params
        )

    async def enable(self, name: str) -> None:
        """
        Enable specified job.

        Args:
            name (str): job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        await self.jenkins._request(
            'POST',
            '/{}/job/{}/enable'.format(folder_name, job_name)
        )

    async def disable(self, name: str) -> None:
        """
        Disable specified job.

        Args:
            name (str): job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        await self.jenkins._request(
            'POST',
            '/{}/job/{}/disable'.format(folder_name, job_name)
        )
