import os
from setuptools import setup

from funcportal.version import __version__


def readme():
    source_root = os.path.dirname(__file__)
    path = os.path.join(source_root, 'README.rst')
    with open(path) as fp:
        return fp.read()


setup(
    name='funcportal',
    version=__version__,
    description='Serve Python functions as web APIs',
    long_description=readme(),
    packages=['funcportal'],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
    ],
    install_requires=[
        'flask',
        'requests',
        'six',
        'pyyaml',
        'rq',
        'redis'
    ],
    entry_points={
        'console_scripts': [
            'funcportal=funcportal.cli:main'
        ]
    }
)
