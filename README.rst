pytest-kafka |pypi| |pyversions| |ci| |docs|
============================================


.. |pypi| image:: https://img.shields.io/pypi/v/pytest-kafka.svg
    :target: https://pypi.org/project/pytest-kafka/

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/pytest-kafka.svg
    :target: https://pypi.org/project/pytest-kafka/

.. |ci| image:: https://gitlab.com/karolinepauls/pytest-kafka/badges/master/pipeline.svg
    :target: https://gitlab.com/karolinepauls/pytest-kafka/pipelines

.. |docs| image:: https://readthedocs.org/projects/pytest-kafka/badge/?version=latest
    :target: https://pytest-kafka.readthedocs.io/en/latest/


Pytest fixture factories for Zookeeper, Kafka server and Kafka consumer.
`Read the API docs <https://pytest-kafka.readthedocs.io>`__.

.. warning::

    ``kafka-python`` doesn't work with Python 3.12. To solve this problem, pytest-kafka, from 0.8.x, no
    longer depends on ``kafka-python``. You can depend on extras: ``pytest-kafka[kafka-python]`` or
    ``pytest-kafka[kafka-python-ng]`` for Python>3.12.

.. code:: python

    from pathlib import Path
    from pytest_kafka import (
        make_zookeeper_process, make_kafka_server, make_kafka_consumer,
        terminate,
    )

    ROOT = Path(__file__).parent
    KAFKA_SCRIPTS = ROOT / 'kafka/bin/'
    KAFKA_BIN = str(KAFKA_SCRIPTS / 'kafka-server-start.sh')
    ZOOKEEPER_BIN = str(KAFKA_SCRIPTS / 'zookeeper-server-start.sh')

    # You can pass a custom teardown function (or parametrise ours). Just don't call it `teardown`
    # or Pytest will interpret it as a module-scoped teardown function.
    teardown_fn = partial(terminate, signal_fn=Popen.kill)
    zookeeper_proc = make_zookeeper_process(ZOOKEEPER_BIN, teardown_fn=teardown_fn)
    kafka_server = make_kafka_server(KAFKA_BIN, 'zookeeper_proc', teardown_fn=teardown_fn)
    kafka_consumer = make_kafka_consumer(
        'kafka_server', seek_to_beginning=True, kafka_topics=['topic'])


This creates 3 fixtures:

#. ``zookeeper_proc`` - Zookeeper process
#. ``kafka_server`` - Kafka process
#. ``kafka_consumer`` - usable ``kafka.KafkaConsumer`` instance


``ZOOKEEPER_BIN`` and ``KAFKA_BIN`` are paths to launch scripts in your Kafka distribution. Check
this project's setup.py to see a way of installing Kafka for development.

It is advised to pass ``seek_to_beginning=True`` because otherwise some messages may not be captured
by the consumer. This requires knowing the topics upfront because without topics there's no
partitions to seek.

Kafka server is known to take a couple of seconds to terminate gracefully. You probably don't
need that, so you can pass ``partial(terminate, signal_fn=Popen.kill)`` to make it killed with
SIGKILL and waited for afterwards.

It's possible to create multiple Kafka fixtures forming a cluster by passing the same Zookeeper
fixture to them. For an example, check the `tests
<https://gitlab.com/karolinepauls/pytest-kafka/blob/master/test_pytest_kafka.py>`__.

Session-scoped fixtures are also available. Consult the `test suite
<https://gitlab.com/karolinepauls/pytest-kafka/blob/master/test_pytest_kafka.py>`__.


System requirements
-------------------

- Python 3.6+
- a JVM that can run Kafka and Zookeeper
- Kafka - https://kafka.apache.org/downloads


Development
-----------

.. code:: sh

   pip install -e .[dev]
   ./pytest_kafka/install.py  # will install kafka to ./kafka


Acknowledgements
----------------

The library has been open-sourced from a codebase belonging to
`Infectious Media <https://infectiousmedia.com>`__.
