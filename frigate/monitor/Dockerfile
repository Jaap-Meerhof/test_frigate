FROM python:3.7.1-alpine3.7

RUN apk add --no-cache bash
SHELL ["/bin/bash", "-c"]

# Install Python dependencies of the Endpoint server
COPY requirements.txt .
RUN  pip install -r requirements.txt

COPY wait-for-it.sh .
RUN chmod +x ./wait-for-it.sh

RUN mkdir /output

COPY monitor_server.py __init__.py graphite_client.py configuration.py ./
