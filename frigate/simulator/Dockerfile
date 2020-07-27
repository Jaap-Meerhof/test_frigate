FROM python:3.7.1-alpine3.7

# xerces 3.1.2
# taken from https://github.com/ojbc/docker/blob/master/apache-shib-sp-base/Dockerfile#L49
COPY xerces-c-3.1.2.tar.gz .
RUN apk add --no-cache g++ musl-dev make autoconf automake libtool bash
RUN tar -xvf xerces-c-3.1.2.tar.gz && \
	cd xerces-c-3.1.2 && \
	./configure --prefix=/opt/shibboleth-sp --disable-netaccessor-libcurl && \
	make && \
	make install && \
	cd .. && rm -rf xerces-c* && \
    ln -s /opt/shibboleth-sp/lib/libxerces-c-3.1.so /usr/lib/libxerces-c.so && \
    ln -s /opt/shibboleth-sp/include/xercesc  /usr/include/xercesc && \
    ln -s /opt/shibboleth-sp/lib/libxerces-c-3.1.so /usr/lib/libxerces-c-3.1.so 

SHELL ["/bin/bash", "-c"]

# SUMO 1.1.0
COPY sumo-1_1_0.tar.gz .
RUN mkdir -p /opt && \
    tar xzvf sumo-1_1_0.tar.gz -C /opt && \
    rm sumo-1_1_0.tar.gz && \
    cd /opt/sumo-1_1_0 && \
    make -f Makefile.cvs && \
    ./configure && \
    make && \
    make install && \
    cd ..

COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh 

# Install Python dependencies of the Simulator
COPY requirements.txt .
RUN  pip install -r requirements.txt

COPY configuration.py __init__.py simulator.py simulator_server.py endpoint_client.py ./