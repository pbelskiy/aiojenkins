from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='aiojenkins',
    version='0.1.1',
    description='Asynchronous library of Jenkins API endpoints based on aiohttp',
    long_description_content_type='text/markdown',
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Petr Belskiy',
    author_email='petr.belskiy@gmail.com',
    keywords=['aiojenkins', 'async jenkins api'],
    url='https://github.com/pbelskiy/aiojenkins',
    download_url='https://pypi.org/project/aiojenkins'
)

install_requires = [
    'aiohttp'
]

if __name__ == '__main__':
    setup(install_requires=install_requires,
          python_requires='>=3.6',
          **setup_args)
