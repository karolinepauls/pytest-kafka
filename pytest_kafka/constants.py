"""Config templates and constants."""


KAFKA_SERVER_CONFIG_TEMPLATE = '''\
reserved.broker.max.id=65535
broker.id={kafka_port}
listeners=PLAINTEXT://:{kafka_port}
log.dirs={kafka_log_dir}
num.partitions=1
# The number of threads lowered to 1 - may boost startup time:
num.recovery.threads.per.data.dir=1
num.network.threads=1
num.io.threads=1
log.retention.hours=1
log.segment.bytes=1073741824
zookeeper.connect=localhost:{zk_port}
zookeeper.connection.timeout.ms=6000
offsets.topic.replication.factor=1
default.replication.factor=1
'''
"""Kafka config template. ``kafka_log_dir``, ```kafka_port``, and ``zk_port`` keys are required."""

ZOOKEEPER_CONFIG_TEMPLATE = '''\
dataDir={zk_data_dir}
clientPort={zk_port}
maxClientCnxns=0
admin.enableServer=false
'''
"""Zookeeper config template. ``zk_data_dir`` and ``zk_port`` keys are required."""

DEFAULT_CONSUMER_TIMEOUT_MS = 500
"""Kafka Consumer timeout in miliseconds."""

DEFAULT_TERMINATION_WAIT_TIMEOUT_SEC = 5
