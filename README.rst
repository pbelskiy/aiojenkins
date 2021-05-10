Async python client for `Jenkins <https://jenkins.io>`_
=======================================================

Asynchronous python library of Jenkins API endpoints based on aiohttp.
Initial version of aiojenkins. 

Public API is still unstable.

Status
------

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

Installation
------------

::

    pip3 install -U aiojenkins


Documentation
-------------

`Read the Docs <https://aiojenkins.readthedocs.io/en/latest/>`_

Usage
-----

Start new build:

.. code:: python

    import asyncio
    import aiojenkins

    jenkins = aiojenkins.Jenkins('http://your_server/jenkins', 'login', 'password')

    async def example():
        await jenkins.builds.start('job_name', dict(parameter='test'))

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(example())
    finally:
        loop.run_until_complete(jenkins.close())
        loop.close()

`Please look at tests directory for more examples. <https://github.com/pbelskiy/aiojenkins/tree/master/tests>`_

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


Or Jenkins 1.554

::

    docker run -d --name jenkins-1.554 --restart always -p 8081:8080 jenkins:1.554

Contributing
------------

Feel free to PR
