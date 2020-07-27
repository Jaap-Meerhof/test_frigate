FROM python:3.7.1-alpine3.7

# gcc is needed to install a dependency of Faust.
# musl-dev is needed to solve the error:
# alpine fatal error: limits.h: No such file or directory
# while compiling a C dependency when installing Faust.
RUN apk add --no-cache gcc musl-dev bash

SHELL ["/bin/bash", "-c"]

# Install SUMO 1.1.0. Only TraCI is needed, so we just copy and uncompress SUMO
COPY sumo-1_1_0.tar.gz .
RUN mkdir /opt && \
    tar xzvf sumo-1_1_0.tar.gz -C /opt && \
    rm sumo-1_1_0.tar.gz

# Install Faust and other Python dependencies of the Stream server
COPY requirements.txt .
RUN  pip install -r requirements.txt

# wait-for-it
COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

# Copy Stream server files
COPY __init__.py stream_worker.py sumo_dijkstra.py configuration.py ./
