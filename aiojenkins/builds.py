import json


class Build:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def start(self, name: str, parameters: dict=None, delay: int=0) -> None:
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

        await self.jenkins._request('POST',
            f'/job/{name}/build',
            params={'delay': delay},
            data=data,
        )

    async def stop(self, name: str, build_id: int) -> None:
        await self.jenkins._request('POST', f'/job/{name}/{build_id}/stop')

    async def delete(self, name: str, build_id: int) -> None:
        await self.jenkins._request('POST', f'/job/{name}/{build_id}/doDelete')

    async def get_info(self, name: str, build_id: int) -> dict:
        response = await self.jenkins._request('GET', f'/job/{name}/{build_id}/api/json')
        return await response.json()
