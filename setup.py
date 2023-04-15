#!/usr/bin/env python3
"""Pytest Kafka fixtures."""
import sys
import subprocess
from os import environ
from pathlib import Path
from typing import List, Tuple
from setuptools import setup, Command  # type: ignore
from setuptools.command.develop import develop  # type: ignore

sys.path.append(str(Path(__file__).parent.joinpath('pytest_kafka')))
from utils import set_up_kafka  # type: ignore # noqa: E402


class CustomDevelop(develop):
    """Install normal and dev dependencies and download Kafka."""

    def run(self):
        """Set up the local dev environment fully."""
        super().run()
        print('* Installing dev dependencies', file=sys.stderr)
        subprocess.check_call(['pip', 'install', '-U', 'pip'])
        subprocess.check_call(['pip', 'install'] + DEV_REQUIREMENTS)

        print('* Setting up Kafka', file=sys.stderr)
        set_up_kafka()


class DownloadKafka(Command):
    """Command to download Kafka."""

    user_options: List[Tuple] = []

    def initialize_options(self):
        """Do nothing, method required by setuptools."""
        pass

    def finalize_options(self):
        """Do nothing, method required by setuptools."""
        pass

    def run(self):
        """Download Kafka."""
        set_up_kafka()


VERSION = '0.5.1'

# Optional suffix for Test PyPI packages.
VERSION_SUFFIX = environ.get('VERSION_SUFFIX', None)
if VERSION_SUFFIX is not None:
    VERSION = '{}.post{}'.format(VERSION, VERSION_SUFFIX)

README_FILE = Path(__file__).resolve().with_name('README.rst')
README = README_FILE.read_text('utf-8')
REQUIREMENTS = [
    'pytest',
    'port_for>=0.4',
    'kafka-python>=1.4.3',
]
DEV_REQUIREMENTS = [
    'flake8',
    'pyflakes>=1.6.0',  # Flake8's version doesn't detect types used in string annotations.
    'flake8-docstrings',
    'flake8_tuple',
    'mypy',
]
DOC_REQUIREMENTS = [
    'Sphinx==2.2.1',
    'sphinx_autodoc_typehints==1.9.0',
    'sphinx-rtd-theme==0.4.3',
]

if __name__ == '__main__':
    setup(
        name='pytest-kafka',
        version=VERSION,
        description='Zookeeper, Kafka server, and Kafka consumer fixtures for Pytest',
        long_description=README,
        classifiers=[
            'Framework :: Pytest',
            'Topic :: Software Development :: Testing',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        keywords='',
        author='Karoline Pauls',
        author_email='code@karolinepauls.com',
        url='https://gitlab.com/karolinepauls/pytest-kafka',
        project_urls={
            "Bug Tracker": 'https://gitlab.com/karolinepauls/pytest-kafka/issues',
            "Documentation": 'https://pytest-kafka.readthedocs.io/',
            "Source Code": 'https://gitlab.com/karolinepauls/pytest-kafka',
        },
        license='MIT',
        packages=['pytest_kafka'],
        package_data={
            'pytest_kafka': ['py.typed'],
        },
        zip_safe=False,
        install_requires=REQUIREMENTS,
        extras_require={
            'dev': DEV_REQUIREMENTS,
            'doc': DOC_REQUIREMENTS,
        },
        cmdclass={
            'kafka': DownloadKafka,
            'develop': CustomDevelop,
        },
        # We don't export fixtures for the user (only fixture factories) but we do declare some
        # fixtures for internal use.
        entry_points={
            'pytest11': ["pytest_kafka = pytest_kafka._fixtures"]
        },
    )
