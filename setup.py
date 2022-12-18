import os
import re

from setuptools import setup

init_file_path = os.path.join(
    os.path.dirname(__file__),
    'aiojenkins/__init__.py'
)

with open(init_file_path, encoding='utf-8') as f:
    try:
        version = re.findall(r"__version__ = '(.*)'", f.read())[0]
    except IndexError:
        raise RuntimeError('Unable to get package version')

with open('README.rst', encoding='utf-8') as f:
    README = f.read()

setup_args = dict(
    name='aiojenkins',
    version=version,
    description='Asynchronous library of Jenkins API based on aiohttp',
    long_description_content_type='text/x-rst',
    long_description=README,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    license='MIT',
    packages=['aiojenkins'],
    package_data={
        '': ['py.typed', '*.pyi'],
    },
    author='Petr Belskiy',
    keywords=['aiojenkins', 'async jenkins api'],
    url='https://github.com/pbelskiy/aiojenkins',
    download_url='https://pypi.org/project/aiojenkins'
)

install_requires = [
    'aiohttp<4.0'
]

if __name__ == '__main__':
    setup(install_requires=install_requires,
          python_requires='>=3.7',
          **setup_args)
