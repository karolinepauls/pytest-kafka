pytest-kafka
============

Pytest fixture factories for Zookeeper, Kafka server and Kafka consumer.


.. code:: python

    zookeeper_proc = make_zookeeper_process(ZOOKEEPER_BIN)
    kafka_server = make_kafka_server(KAFKA_BIN, 'zookeeper_proc')
    kafka_consumer = make_kafka_consumer(
        'kafka_server', seek_to_beginning=True, kafka_topics=['topic'])


This creates 3 fixtures:

#. ``zookeeper_proc`` - Zookeeper process
#. ``kafka_server`` - Kafka process
#. ``kafka_consumer`` - usable ``kafka.KafkaConsumer`` instance


``ZOOKEEPER_BIN`` and ``KAFKA_BIN`` are paths to launch scripts in your Kafka distribution. Check
this project's setup.py to see a way of installing Kafka for development.

It's advised to pass ``seek_to_beginning=True`` because otherwise some messages may not be captured
by the consumer. This requires knowing the topics upfront because without topics there's no
partitions to seek.

It's possible to create multiple Kafka fixtures forming a cluster by passing the same Zookeeper
fixture to them. For an example, check the tests.

Session-scoped fixtures are also available. Consult the test suite.


System requirements
-------------------

- Python 3.5+
- JVM
- Kafka - https://kafka.apache.org/downloads


Development
-----------

Execute ``./setup.py develop`` in a virtualenv. This will take care of:

- installing dependencies
- updating pip
- installing dev dependencies
- installing Kafka to the project dir (for development only)


Acknowledgements
----------------

The library has been open-sourced from a codebase belonging to
`Infectious Media <https://infectiousmedia.com>`__.
