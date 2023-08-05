import os
import re
import sys

from setuptools import setup, find_packages

if sys.version_info < (3,6):
    sys.exit('Sorry, Python < 3.6 is not supported')


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__main__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.rst') as f:
    readme = f.read()

setup(
    name='tibiawikisql',
    version=get_version("tibiawikisql"),
    author='Galarzaa90',
    author_email="allan.galarza@gmail.com",
    url='https://github.com/Galarzaa90/tibiawiki-sql',
    license='Apache 2.0',
    install_requires=requirements,
    description="Python script that generates a SQLite database from TibiaWiki articles",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Internet',
        'Topic :: Utilities'
    ]
)
