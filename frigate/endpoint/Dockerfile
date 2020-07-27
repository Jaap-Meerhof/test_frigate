FROM python:3.7.1-alpine3.7

RUN apk add --no-cache bash
SHELL ["/bin/bash", "-c"]

# Install SUMO 1.1.0. Only TraCI is needed, so we just copy and uncompress SUMO
COPY sumo-1_1_0.tar.gz .
RUN mkdir /opt && \
    tar xzvf sumo-1_1_0.tar.gz -C /opt && \
    rm sumo-1_1_0.tar.gz

# Install Python dependencies of the Endpoint server
COPY requirements.txt .
RUN  pip install -r requirements.txt

COPY wait-for-it.sh .
RUN chmod +x ./wait-for-it.sh

COPY endpoint_server.py __init__.py configuration.py ./
