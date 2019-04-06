"""Test setup."""
from typing import Optional
import pytest  # type: ignore
from test_pytest_kafka import test_custom_kill


EXPECTED_TEARDOWN_ON_KILL = 0.2
test_custom_kill_duration = None  # type: Optional[float]


def _test_custom_kill_slow_teardown() -> bool:
    return (test_custom_kill_duration is not None
            and test_custom_kill_duration > EXPECTED_TEARDOWN_ON_KILL)


def pytest_runtest_makereport(item, call):
    """Record teardown time of `test_custom_kill`."""
    if item.function == test_custom_kill and call.when == 'teardown':
        global test_custom_kill_duration
        test_custom_kill_duration = call.stop - call.start


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Report `test_custom_kill` teardown time."""
    if _test_custom_kill_slow_teardown():
        terminalreporter.write_sep(
            '=',
            "`test_custom_kill` didn't tear down in time",
            bold=True, red=True
        )
        terminalreporter.write_line(
            '`test_custom_kill` is expected to tear down in under {} but it took {:.2f} sec'.format(
                EXPECTED_TEARDOWN_ON_KILL, test_custom_kill_duration),
            red=True, bold=True
        )


def pytest_sessionfinish(session, exitstatus):
    """Exit with an error if `test_custom_kill` didn't tear down in time."""
    if _test_custom_kill_slow_teardown():
        session.exitstatus = 1
