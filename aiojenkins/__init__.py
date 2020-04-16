import asyncio
import aiohttp

from urllib.parse import urlencode
from functools import partial


class Jenkins:

    def __init__(self, host, login, password):
        self.host = host
        self.auth = aiohttp.BasicAuth(login, password)

    async def build_job(self, name, parameters):
        url = '{host}/job/{name}/buildWithParameters?{data}'.format(
            host=self.host,
            name=name,
            data=urlencode(parameters),
        )

        async with aiohttp.ClientSession() as session:
            await session.post(url, auth=self.auth)


if __name__ == '__main__':
    jenkins = Jenkins('http://localhost:8080', 'admin', 'admin')

    asyncio.run(jenkins.build_job('test', dict(arg=1)))
