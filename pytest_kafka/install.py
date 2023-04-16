"""Utility methods for downloading Kafka locally."""
import contextlib
import shutil
import sys
import tarfile
import typing
import urllib.request
from pathlib import Path


KAFKA_URL = 'https://downloads.apache.org/kafka/3.2.3/kafka_2.13-3.2.3.tgz'
KAFKA_TAR = 'kafka.tgz'
KAFKA_DIR = 'kafka'
KAFKA_TAR_ROOTDIR = 'kafka_2.13-3.2.3/'


def set_up_kafka(kafka_url: str = KAFKA_URL,
                 extract_location: str = '.',
                 kafka_dir: str = KAFKA_DIR,
                 kafka_tar: str = KAFKA_TAR,
                 kafka_tar_rootdir: str = KAFKA_TAR_ROOTDIR):
    """
    Clean, download Kafka from an official mirror and untar it.

    The `kafka_dir`, `kafka_tar` and `kafka_tar_rootdir` arguments are reletive to the
    `extract_location` argument suh that calling
    `setup_kafka(extract_location='/opt/local', kafka_dir='my_kafka')`
    will result in Kafka being installed into `/opt/local/my_kafka`
    """
    extract_location_ = Path(extract_location).resolve()
    kafka_tar_rootdir_ = extract_location_ / kafka_tar_rootdir
    kafka_dir_ = extract_location_ / kafka_dir
    kafka_tar_ = extract_location_ / kafka_tar

    clean_kafka(kafka_dir=kafka_dir_, kafka_tar_rootdir=kafka_tar_rootdir_, kafka_tar=kafka_tar_)

    print('* Downloading Kafka', file=sys.stderr)
    urllib.request.urlretrieve(kafka_url, kafka_tar_)

    print('* Unpacking Kafka', file=sys.stderr)
    with tarfile.open(kafka_tar_, 'r') as f:
        f.extractall(extract_location_)

    print('* Renaming:', kafka_tar_rootdir_, '→', kafka_dir_, file=sys.stderr)
    kafka_tar_rootdir_.rename(kafka_dir_)

    kafka_tar_.unlink()


def clean_kafka(kafka_dir: typing.Union[str, Path] = KAFKA_DIR,
                kafka_tar_rootdir: typing.Union[str, Path] = KAFKA_TAR_ROOTDIR,
                kafka_tar: typing.Union[str, Path] = KAFKA_TAR):
    """Clean whatever `set_up_kafka` may create."""
    shutil.rmtree(kafka_dir, ignore_errors=True)
    shutil.rmtree(kafka_tar_rootdir, ignore_errors=True)
    with contextlib.suppress(FileNotFoundError):
        Path(kafka_tar).unlink()


if __name__ == '__main__':
    set_up_kafka()
