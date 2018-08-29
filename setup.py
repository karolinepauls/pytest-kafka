#!/usr/bin/env python3
"""Pytest Kafka fixtures."""
import sys
import subprocess
import contextlib
import shutil
import urllib.request
import tarfile
from pathlib import Path
from setuptools import setup  # type: ignore
from setuptools.command.develop import develop  # type: ignore


KAFKA_URL = (
    'https://www.mirrorservice.org/sites/ftp.apache.org/kafka/1.1.1/kafka_2.11-1.1.1.tgz')
KAFKA_TAR = 'kafka.tgz'
KAFKA_TAR_ROOTDIR = 'kafka_2.11-1.1.1'
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
        subprocess.check_call(['pip', 'install', '.[dev]'])

        print('* Setting up Kafka', file=sys.stderr)
        set_up_kafka()


README_FILE = Path(__file__).resolve().with_name('README.rst')
README = README_FILE.read_text('utf-8')
REQUIREMENTS = [
    'pytest',
    'port_for>=0.4',
    'kafka>=1.3.5',
]
DEV_REQUIREMENTS = [
    'flake8',
    'pyflakes>=1.6.0',  # Flake8's version doesn't detect types used in string annotations.
    'flake8-docstrings',
    'flake8_tuple',
    'mypy',
]

setup(
    name='pytest-kafka',
    version='0.0.2',
    description='Zookeeper, Kafka server, and Kafka consumer fixtures for Pytest',
    long_description=README,
    classifiers=[
        'Framework :: Pytest',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='',
    author='Karoline Pauls',
    author_email='code@karolinepauls.com',
    url='https://gitlab.com/karolinepauls/pytest-kafka',
    license='MIT',
    packages=['pytest_kafka'],
    package_data={
        'pytest_kafka': ['py.typed'],
    },
    zip_safe=False,
    install_requires=REQUIREMENTS,
    extras_require={'dev': DEV_REQUIREMENTS},
    cmdclass={
        'develop': CustomDevelop,
    },
    # We don't export fixtures for the user (only fixture factories) but we do declare some fixtures
    # for internal use.
    entry_points={
        'pytest11': ["pytest_kafka = pytest_kafka._fixtures"]
    },
)
