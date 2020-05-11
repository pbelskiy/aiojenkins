# aiojenkins

![Tests](https://github.com/pbelskiy/aiojenkins/workflows/Tests/badge.svg)
![Coveralls github](https://img.shields.io/coveralls/github/pbelskiy/aiojenkins?label=Coverage)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aiojenkins?color=1&label=Downloads)

Asynchronous python library of Jenkins API endpoints based on aiohttp 🥳

Initial version of aiojenkins. Public API is still unstable (work is in progress)

Minimal Python version is 3.6 due async await and f-strings.

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
    await jenkins.build_job('job_name', dict(parameter='test'))

asyncio.run(example())
```

__Please look at tests directory for more examples.__

## Testing

Currently tests aren't using any mocking.
I am testing locally with dockerized Jenkins ver. 2.60.3

Prerequisites: `docker, pytest pytest-cov pytest-asyncio`

```sh
docker run -p 8080:8080 jenkins
python3 -m pytest -v --cov=aiojenkins --cov-report=term --cov-report=html
```

## Contributing

Feel free to PR :)
