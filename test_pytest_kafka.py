"""
Pytest-kafka tests.

Can serve as examples of Pytest-kafka usage.
"""
from pathlib import Path
from typing import Tuple, TYPE_CHECKING
from functools import partial
from os import environ
from subprocess import Popen
from time import sleep
import pytest  # type: ignore
from kafka import KafkaProducer, KafkaConsumer  # type: ignore
from pytest_kafka import make_zookeeper_process, make_kafka_server, make_kafka_consumer, terminate
if TYPE_CHECKING:
    # Don't break anything else than typechecking if pytest changes.
    from _pytest.fixtures import SubRequest  # type: ignore  # noqa


ROOT = Path(__file__).parent

# Optionally use an alternate location for Kafka when the `KAFKA_SCRIPTS` env var is set
KAFKA_SCRIPTS = Path(environ.get('KAFKA_SCRIPTS', str(ROOT / 'kafka/bin/')))

KAFKA_BIN = str(KAFKA_SCRIPTS / 'kafka-server-start.sh')
ZOOKEEPER_BIN = str(KAFKA_SCRIPTS / 'zookeeper-server-start.sh')

TOPIC = 'abc'

# 2 independent basic fixture sets.
zookeeper_proc = make_zookeeper_process(ZOOKEEPER_BIN)
kafka_server = make_kafka_server(KAFKA_BIN, 'zookeeper_proc')
kafka_consumer = make_kafka_consumer('kafka_server', seek_to_beginning=True, kafka_topics=[TOPIC])

zookeeper_proc_2 = make_zookeeper_process(ZOOKEEPER_BIN)
kafka_server_2 = make_kafka_server(KAFKA_BIN, 'zookeeper_proc_2')
kafka_consumer_2 = make_kafka_consumer('kafka_server', seek_to_beginning=True, kafka_topics=[TOPIC])

# Zookeeper shared with `kafka_server`.
kafka_server_same_zk = make_kafka_server(KAFKA_BIN, 'zookeeper_proc')
kafka_consumer_same_zk = make_kafka_consumer(
    'kafka_server_same_zk', seek_to_beginning=True, kafka_topics=[TOPIC])

# ZK and Kafka immediately killed with SIGKILL on teardown.
# Don't call `teardown_fn` `teardown` or Pytest will try to run it on module teardown.
teardown_fn = partial(terminate, signal_fn=Popen.kill)
zookeeper_proc_kill = make_zookeeper_process(ZOOKEEPER_BIN, teardown_fn=teardown_fn)
kafka_server_kill = make_kafka_server(KAFKA_BIN, 'zookeeper_proc_kill', teardown_fn=teardown_fn)
kafka_consumer_kill = make_kafka_consumer(
    'kafka_server_kill', seek_to_beginning=True, kafka_topics=[TOPIC])

# Session-scoped fixture set.
zookeeper_proc_session = make_zookeeper_process(ZOOKEEPER_BIN, scope='session')
kafka_server_session = make_kafka_server(KAFKA_BIN, 'zookeeper_proc_session', scope='session')
# The consumer can be either function- or session-scoped.
kafka_consumer_session_function = make_kafka_consumer(
    'kafka_server_session', seek_to_beginning=True, kafka_topics=[TOPIC])
kafka_consumer_session_session = make_kafka_consumer(
    'kafka_server_session', seek_to_beginning=True, kafka_topics=[TOPIC], scope='session')


def write_to_kafka(kafka_server: Tuple[Popen, int], message: bytes) -> None:
    """Write a message to kafka_server."""
    _, kafka_port = kafka_server
    producer = KafkaProducer(bootstrap_servers='localhost:{}'.format(kafka_port))
    producer.send(TOPIC, message)
    producer.flush()


def write_and_read(kafka_server: Tuple[Popen, int], kafka_consumer: KafkaConsumer) -> None:
    """Write to kafka_server, consume with kafka_consumer."""
    message = b'msg'
    write_to_kafka(kafka_server, message)
    consumed = list(kafka_consumer)
    assert len(consumed) == 1
    assert consumed[0].topic == TOPIC
    assert consumed[0].value == message


def test_2_fixture_sets(kafka_server: Tuple[Popen, int], kafka_consumer: KafkaConsumer,
                        kafka_server_2: Tuple[Popen, int], kafka_consumer_2: KafkaConsumer):
    """Test 2 sets of fixtures."""
    write_and_read(kafka_server, kafka_consumer)
    write_and_read(kafka_server_2, kafka_consumer_2)


def test_2_kafkas_shared_zookeeper_cluster(
    kafka_server: Tuple[Popen, int], kafka_consumer: KafkaConsumer,
    kafka_server_same_zk: Tuple[Popen, int], kafka_consumer_same_zk: KafkaConsumer
):
    """Test creating a cluster of 2 Kafkas both talking to a single Zookeeper."""
    assert (
        kafka_consumer.config['bootstrap_servers'] !=
        kafka_consumer_same_zk.config['bootstrap_servers']
    ), 'Consumers should bootstrap from different kafkas'

    message_1 = b'pooh'
    message_2 = b'tiger'
    write_to_kafka(kafka_server, message_1)
    write_to_kafka(kafka_server_same_zk, message_2)
    consumed_1 = list(kafka_consumer)
    consumed_2 = list(kafka_consumer_same_zk)
    messages_1 = [m.value for m in consumed_1]
    messages_2 = [m.value for m in consumed_2]
    excepted_messages = [message_1, message_2]  # Both messages visible for both consumers.
    assert messages_1 == messages_2 == excepted_messages


def test_custom_kill(kafka_server_kill):
    """
    Test supplying custom process teardown function.

    Teardown timing of this test is checked by hooks in conftest.
    """
    pass


@pytest.fixture(scope='session')
def wrote_something_to_kafka(
    kafka_server_session: Tuple[Popen, int],
    kafka_consumer_session_session: KafkaConsumer,
) -> None:
    """Write a message to Kafka using a session-scoped consumer fixture."""
    written_before = list(kafka_consumer_session_session)
    assert len(written_before) == 0
    write_and_read(kafka_server_session, kafka_consumer_session_session)


def test_session_scoped_kafka(
    kafka_server_session: Tuple[Popen, int],
    kafka_consumer_session_function: KafkaConsumer,
    kafka_consumer_session_session: KafkaConsumer,
    wrote_something_to_kafka: None,
):
    """
    Use a session-scoped fixture set.

    Place this test last so its session-scoped teardown doesn't disturb timings of some other test.
    """
    # Ugly sleep. Need to investigate. https://gitlab.com/karolinepauls/pytest-kafka/issues/3
    # 0.05 seems to be the boundary. Nothing happens in Kafka consumer logs though.
    sleep(0.5)
    written_in_setup = list(kafka_consumer_session_function)
    kafka_consumer_session_session.seek_to_beginning()
    written_in_setup_session = list(kafka_consumer_session_session)
    assert len(written_in_setup) == 1
    assert len(written_in_setup_session) == 1
