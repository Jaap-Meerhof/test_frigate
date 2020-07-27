FROM openjdk:8u212-jre-alpine

# copy Kafka from disk and install it
COPY kafka_2.12-2.4.0.tgz .
RUN apk add --no-cache bash make python3 && \
    tar -xzf kafka_2.12-2.4.0.tgz -C /opt && \
    rm kafka_2.12-2.4.0.tgz && \
    chmod +x /opt/kafka_2.12-2.4.0/bin/kafka-server-start.sh

COPY Makefile wait-for-it.sh kafka-setup.sh ./
RUN chmod +x wait-for-it.sh
RUN chmod +x kafka-setup.sh

SHELL ["/bin/bash", "-c"]