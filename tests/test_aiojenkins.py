#!/usr/bin/python3

import asyncio

from aiojenkins import Jenkins

jenkins = Jenkins('http://localhost:8080', 'admin', 'admin')


def test_build_job():
    asyncio.run(jenkins.build_job('test', dict(arg=1)))


def test_stop_build():
    asyncio.run(jenkins.stop_build('test', 1))


def test_delete_build():
    asyncio.run(jenkins.delete_build('test', 2))


def test_get_job_info():
    asyncio.run(jenkins.get_job_info('test'))


def test_get_build_info():
    asyncio.run(jenkins.get_build_info('test', 2260))


def test_get_status():
    asyncio.run(jenkins.get_nodes())


def test_get_nodes():
    asyncio.run(jenkins.get_nodes())
