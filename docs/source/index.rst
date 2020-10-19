.. aiojenkins documentation master file, created by
   sphinx-quickstart on Mon Oct 19 15:22:37 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================
Welcome to aiojenkins
=====================

Asynchronous python library of Jenkins API endpoints based on aiohttp.

.. _GitHub: https://github.com/pbelskiy/aiojenkins


Key features
============

- Jenkins instance management
- Nodes management
- Jobs management
- Views management
- Helpers for XML config generation

.. _aiojenkins-installation:

Installation
============

.. code-block:: bash

   $ pip3 install aiojenkins


Basic example
=============

.. code-block:: python

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


Source code
===========

The project is hosted on GitHub_ and uses GitHub actions for continuous integration.


Dependencies
============

- Python 3.5+
- *aiohttp*


Contributing
============

Feel free to PR and open new issues


Authors and license
===================

The ``aiojenkins`` package is written by Petr Belskiy.

It's *MIT* licensed and freely available.

Feel free to improve this package and send a pull request to GitHub_.


Table of contents
=================

.. toctree::
   :name: mastertoc
   :maxdepth: 2

   jobs
