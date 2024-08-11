#!/usr/bin/env python3
"""Utility methods for downloading Kafka locally."""
import contextlib
import shutil
import os
import tarfile
import typing
import logging
import urllib.request
from urllib.parse import urlsplit
from pathlib import Path

log = logging.getLogger(__name__)

KAFKA_URL = 'https://archive.apache.org/dist/kafka/3.2.3/kafka_2.13-3.2.3.tgz'
KAFKA_TAR = 'kafka.tgz'
KAFKA_DIR = 'kafka'


def expected_archive_root_dir(kafka_url: str) -> str:
    """
    Determine the expected archive root directory name.

    >>> url = 'https://archive.apache.org/dist/kafka/3.8.0/kafka_2.13-3.8.0.tgz'
    >>> expected_archive_root_dir(url)
    'kafka_2.13-3.8.0'
    """
    url_path = urlsplit(kafka_url).path
    return Path(url_path).with_suffix('').name


def set_up_kafka(kafka_url: str = KAFKA_URL,
                 extract_location: str = '.',
                 kafka_dir: str = KAFKA_DIR,
                 kafka_tar: str = KAFKA_TAR,
                 kafka_tar_rootdir: typing.Optional[str] = None) -> None:
    """
    Clean, download Kafka from an official mirror and untar it.

    :param kafka_url: URL to download Kafka archive from
    :param extract_location: local directory to extract the Kafka archive to
    :param kafka_dir: directory name to rename the in-archive Kafka distribution directory to
    :param kafka_tar: file name of the downloaded Kafka archive
    :param kafka_tar_rootdir: expected name of the root directory in the Kafka archive, which
        contains the Kafka distribution. If None, it will be the URL file name without a suffix.

    The `kafka_dir`, `kafka_tar` and `kafka_tar_rootdir` arguments are relative to the
    `extract_location` argument so that calling
    ``setup_kafka(extract_location='/opt/local', kafka_dir='my_kafka')``
    will result in Kafka being installed into ``/opt/local/my_kafka``
    """
    extract_path = Path(extract_location).resolve()
    downloaded_tarfile = extract_path / kafka_tar

    if kafka_tar_rootdir is None:
        kafka_tar_rootdir = expected_archive_root_dir(kafka_url)

    kafka_tar_rootdir_path = extract_path / kafka_tar_rootdir
    target_kafka_dir = extract_path / kafka_dir

    clean_kafka(
        kafka_dir=target_kafka_dir,
        kafka_tar_rootdir=kafka_tar_rootdir_path,
        kafka_tar=downloaded_tarfile,
    )

    log.info('Downloading Kafka from %r to %s', kafka_url, downloaded_tarfile)
    urllib.request.urlretrieve(kafka_url, downloaded_tarfile)

    log.info('Unpacking %s to %s', downloaded_tarfile, extract_path)
    with tarfile.open(downloaded_tarfile, 'r') as f:
        f.extractall(extract_path)

    log.info('Renaming: %s → %s', kafka_tar_rootdir_path, target_kafka_dir)
    kafka_tar_rootdir_path.rename(target_kafka_dir)

    downloaded_tarfile.unlink()


def clean_kafka(kafka_dir: typing.Union[str, Path] = KAFKA_DIR,
                kafka_tar_rootdir: typing.Union[str, Path, None] = None,
                kafka_tar: typing.Union[str, Path] = KAFKA_TAR) -> None:
    """Clean whatever ``set_up_kafka`` may create."""
    if kafka_tar_rootdir is None:
        kafka_tar_rootdir = expected_archive_root_dir(KAFKA_URL)

    shutil.rmtree(kafka_dir, ignore_errors=True)
    shutil.rmtree(kafka_tar_rootdir, ignore_errors=True)
    with contextlib.suppress(FileNotFoundError):
        Path(kafka_tar).unlink()


def _main() -> None:
    logging.basicConfig(level=logging.INFO)

    kafka_url = os.environ.get('PYTEST_KAFKA_KAFKA_URL', KAFKA_URL)
    extract_location = os.environ.get('PYTEST_KAFKA_EXTRACT_LOCATION', '.')
    kafka_tar = os.environ.get('PYTEST_KAFKA_KAFKA_TAR', KAFKA_TAR)
    kafka_dir = os.environ.get('PYTEST_KAFKA_KAFKA_DIR', KAFKA_DIR)
    kafka_tar_rootdir = os.environ.get('PYTEST_KAFKA_KAFKA_TAR_ROOTDIR', None)

    set_up_kafka(
        kafka_url=kafka_url,
        extract_location=extract_location,
        kafka_tar=kafka_tar,
        kafka_dir=kafka_dir,
        kafka_tar_rootdir=kafka_tar_rootdir,
    )


if __name__ == '__main__':
    _main()
