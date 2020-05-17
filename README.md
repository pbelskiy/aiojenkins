# aiojenkins

![Tests](https://github.com/pbelskiy/aiojenkins/workflows/Tests/badge.svg)
![Coveralls github](https://img.shields.io/coveralls/github/pbelskiy/aiojenkins?label=Coverage)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aiojenkins?color=1&label=Downloads)

Asynchronous python library of Jenkins API endpoints based on aiohttp 🥳

Initial version of aiojenkins. Public API is still unstable (work is in progress)

Minimal Python version is 3.6 due async await and f-strings.

The package is tested on below matrix:
- CPython: 3.6, 3.7, 3.8
- Jenkins LTS: 1.554, 2.60.3, latest

## Installation

```sh
pip install aiojenkins
```

## Usage

Start new build:
```python
import asyncio
import aiojenkins

async def example():
    jenkins = aiojenkins.Jenkins('http://your_server/jenkins', 'login', 'password')
    await jenkins.builds.start('job_name', dict(parameter='test'))

asyncio.run(example())
```

__Please look at tests directory for more examples.__

## Testing

Currently tests aren't using any mocking.
I am testing locally with dockerized LTS Jenkins ver. 2.222.3

Prerequisites: `docker, pytest pytest-cov pytest-asyncio`

```sh
docker run -d --name jenkins --restart always -p 8080:8080 jenkins/jenkins:lts
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
python3 -m pytest -v --cov=aiojenkins --cov-report=term --cov-report=html
```

## Contributing

Feel free to PR :)
