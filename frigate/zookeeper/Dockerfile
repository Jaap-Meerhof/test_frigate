FROM openjdk:8u212-jre-alpine

# copy Kafka from disk and install it
COPY kafka_2.12-2.4.0.tgz .
RUN apk add --no-cache bash && \
    tar -xzf kafka_2.12-2.4.0.tgz -C /opt && \
    rm kafka_2.12-2.4.0.tgz && \
    chmod +x /opt/kafka_2.12-2.4.0/bin/zookeeper-server-start.sh

COPY zookeeper.properties ./

SHELL ["/bin/bash", "-c"]