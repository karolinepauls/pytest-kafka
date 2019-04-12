#!/usr/bin/env python3
"""Pytest Kafka fixtures."""
import sys
import subprocess
import contextlib
import shutil
import urllib.request
import tarfile
from pathlib import Path
from typing import List, Tuple
from setuptools import setup, Command  # type: ignore
from setuptools.command.develop import develop  # type: ignore


KAFKA_URL = 'https://www.mirrorservice.org/sites/ftp.apache.org/kafka/2.2.0/kafka_2.12-2.2.0.tgz'
KAFKA_TAR = 'kafka.tgz'
KAFKA_TAR_ROOTDIR = 'kafka_2.12-2.2.0'
KAFKA_DIR = 'kafka'


def set_up_kafka():
    """Clean, download Kafka from an official mirror and untar it."""
    clean_kafka()

    print('* Downloading Kafka', file=sys.stderr)
    urllib.request.urlretrieve(KAFKA_URL, KAFKA_TAR)

    print('* Unpacking Kafka', file=sys.stderr)
    with tarfile.open(KAFKA_TAR, 'r') as f:
        f.extractall()

    print('* Renaming:', KAFKA_TAR_ROOTDIR, '→', KAFKA_DIR, file=sys.stderr)
    Path(KAFKA_TAR_ROOTDIR).rename(KAFKA_DIR)
    Path(KAFKA_TAR).unlink()


def clean_kafka():
    """Clean whatever `set_up_kafka` may create."""
    shutil.rmtree(KAFKA_DIR, ignore_errors=True)
    shutil.rmtree(KAFKA_TAR_ROOTDIR, ignore_errors=True)
    with contextlib.suppress(FileNotFoundError):
        Path(KAFKA_TAR).unlink()


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

    user_options = []  # type: List[Tuple]

    def initialize_options(self):
        """Do nothing, method required by setuptools."""
        pass

    def finalize_options(self):
        """Do nothing, method required by setuptools."""
        pass

    def run(self):
        """Download Kafka."""
        set_up_kafka()


VERSION = '0.3.1'
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
    'Sphinx==1.7.8',
    'sphinx-autodoc-annotation==1.0.post1',
    'sphinx-rtd-theme==0.4.1',
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
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
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
