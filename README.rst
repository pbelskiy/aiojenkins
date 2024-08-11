Async python client for `Jenkins <https://jenkins.io>`_
=======================================================

|Build status|
|Docs status|
|Coverage status|
|Version status|
|Downloads status|

.. |Build Status|
   image:: https://github.com/pbelskiy/aiojenkins/workflows/Tests/badge.svg
.. |Docs status|
   image:: https://readthedocs.org/projects/aiojenkins/badge/?version=latest
.. |Coverage status|
   image:: https://img.shields.io/coveralls/github/pbelskiy/aiojenkins?label=Coverage
.. |Version status|
   image:: https://img.shields.io/pypi/pyversions/aiojenkins?label=Python
.. |Downloads status|
   image:: https://img.shields.io/pypi/dm/aiojenkins?color=1&label=Downloads


Asynchronous python package of Jenkins API endpoints based on aiohttp.

----

Also pay attention to brand new package with same API set but with sync and async interfaces:

https://github.com/pbelskiy/ujenkins

Installation
------------

.. code:: shell

    pip3 install aiojenkins

Usage
-----

Start new build:

.. code:: python

    import asyncio
    import aiojenkins

    async def example():
        async with aiojenkins.Jenkins('http://your_server/jenkins', 'user', 'password') as jenkins:
            await jenkins.builds.start('job_name', {'parameter':'test'})

    asyncio.run(example())

`Please look at tests directory for more examples. <https://github.com/pbelskiy/aiojenkins/tree/master/tests>`_

Documentation
-------------

`Read the Docs <https://aiojenkins.readthedocs.io/en/latest/>`_

Testing
-------

Currently tests aren't using any mocking.
I am testing locally with dockerized LTS Jenkins ver. 2.222.3

Prerequisites: `docker, tox`

::

    docker run -d --name jenkins --restart always -p 8080:8080 jenkins/jenkins:lts
    docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
    chromium http://localhost:8080  # create admin:admin
    tox

Contributing
------------

Feel free to PR
