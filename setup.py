from setuptools import setup

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='aiojenkins',
    version='0.5.3',
    description='Asynchronous library of Jenkins API based on aiohttp',
    long_description_content_type='text/markdown',
    long_description=README,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    license='MIT',
    packages=['aiojenkins'],
    package_data={
        '': ['py.typed', '*.pyi'],
    },
    author='Petr Belskiy',
    author_email='petr.belskiy@gmail.com',
    keywords=['aiojenkins', 'async jenkins api'],
    url='https://github.com/pbelskiy/aiojenkins',
    download_url='https://pypi.org/project/aiojenkins'
)

install_requires = [
    'aiohttp<4.0'
]

if __name__ == '__main__':
    setup(install_requires=install_requires,
          python_requires='>=3.5',
          **setup_args)
