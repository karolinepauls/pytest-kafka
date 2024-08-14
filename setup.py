#!/usr/bin/env python3
"""Pytest Kafka fixtures."""
from os import environ
from pathlib import Path
from setuptools import setup  # type: ignore


VERSION = '0.8.1'

# Optional suffix for Test PyPI packages.
VERSION_SUFFIX = environ.get('VERSION_SUFFIX', None)
if VERSION_SUFFIX is not None:
    VERSION = '{}.post{}'.format(VERSION, VERSION_SUFFIX)

README_FILE = Path(__file__).resolve().with_name('README.rst')
README = README_FILE.read_text('utf-8')
REQUIREMENTS = [
    'pytest',
    'port_for>=0.4',
]
DEV_REQUIREMENTS = [
    'flake8',
    'pyflakes>=1.6.0',  # Flake8's version doesn't detect types used in string annotations.
    'flake8-docstrings',
    'flake8_tuple',
    'mypy',
]
DOC_REQUIREMENTS = [
    'Sphinx==7.4.7',
    'sphinx-rtd-theme==2.0.0',
]
KAFKA_PYTHON_REQUIREMENT = [
    'kafka-python>=1.4.3',
]
KAFKA_PYTHON_NG_REQUIREMENT = [
    'kafka-python-ng>=2.2.2',
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
            'kafka-python': KAFKA_PYTHON_REQUIREMENT,
            'kafka-python-ng': KAFKA_PYTHON_NG_REQUIREMENT,
            'dev': DEV_REQUIREMENTS,
            'doc': DOC_REQUIREMENTS,
        },
        # We don't export fixtures for the user (only fixture factories) but we do declare some
        # fixtures for internal use.
        entry_points={
            'pytest11': ["pytest_kafka = pytest_kafka._fixtures"],
        },
    )
