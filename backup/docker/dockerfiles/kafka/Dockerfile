FROM openjdk:8u212-jre-alpine

ARG kafka_version=2.4.0
ARG scala_version=2.12 
ARG name_server=192.168.43.1

ENV KAFKA_VERSION=$kafka_version
ENV SCALA_VERSION=$scala_version
ENV NAME_SERVER=$name_server

# copy Kafka from disk
COPY kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz .
RUN echo "nameserver ${NAME_SERVER}" >> /etc/resolv.conf \    
    && apk add --no-cache bash \
    && tar -xzf kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -C /opt \
    && rm kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz \
    && chmod +x /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION}/bin/kafka-server-start.sh

# download Kafka
#RUN echo "nameserver ${NAME_SERVER}" >> /etc/resolv.conf \    
#    && apk add --no-cache bash \
#    && wget https://www-us.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz \
#    && tar -xzf kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -C /opt \
#    && rm kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz \
#    && chmod +x /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION}/bin/kafka-server-start.sh

WORKDIR /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION}
 
ENTRYPOINT bash bin/kafka-server-start.sh config/server.properties
