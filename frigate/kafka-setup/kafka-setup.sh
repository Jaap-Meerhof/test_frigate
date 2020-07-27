#!/bin/bash

echo "KAFKA_HOME=$KAFKA_HOME"
echo "TOPIC_PARTITIONS=$TOPIC_PARTITIONS"
echo "info creating kafka topics ..."
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic qtable-entry-init-topic
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic qtable-entry-update-topic
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic vehicle-entry-init-topic
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic vehicle-status-topic
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic vehicle-arrival-topic
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic edge-change-topic
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic stream-service-app-qtable-changelog
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper frigate-zookeeper:2181 --replication-factor 1 --partitions $TOPIC_PARTITIONS --topic stream-service-app-vehicle-table-changelog
echo "start Python HTTP server at 8080"
python3 -m http.server 8080 --bind 0.0.0.0 
echo "exited python3 HTTP server!"