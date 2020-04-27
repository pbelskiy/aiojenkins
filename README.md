# aiojenkins

![Tests](https://github.com/pbelskiy/aiojenkins/workflows/Python%20package/badge.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aiojenkins?color=1&label=Downloads)

Asynchronous python library of Jenkins API endpoints based on aiohttp 🥳

Initial version of aiojenkins. Public API is still unstable (work is in progress)

### Examples

Start new build:
```python
import asyncio
import aiojenkins

async def example():
    jenkins = aiojenkins.Jenkins('http://your_server/jenkins', 'login', 'password')
    await jenkins.build_job('job_name', dict(parameter='test'))

asyncio.run(example())
```
