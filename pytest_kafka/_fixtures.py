"""
Fixtures used by pytest-kafka.

Dev note: This file is referenced by the 'pytest11' entry point and for some reason requires
./setup.py develop to be executed so Pytest can pick up changes.
"""
from pathlib import Path
from typing import TYPE_CHECKING
import pytest  # type: ignore
if TYPE_CHECKING:
    # Don't break anything else than typechecking if pytest changes.
    from _pytest.tmpdir import TempdirFactory  # type: ignore  # noqa


@pytest.fixture
def tmpdir_path(tmpdir) -> Path:
    """Wrap pytest's `tmpdir` fixture to return a Path object."""
    return Path(str(tmpdir))


@pytest.fixture(scope='session')
def session_tmpdir_path(tmpdir_factory: 'TempdirFactory') -> Path:
    """Create a tempdir and return it."""
    return Path(str(tmpdir_factory.mktemp('session-scoped')))
