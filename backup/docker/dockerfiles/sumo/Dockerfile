FROM python:3.7.1-alpine3.7

ARG name_server=192.168.43.1
ARG sumo_version=1_1_0

ENV NAME_SERVER=$name_server \
    SUMO_VERSION=$sumo_version

RUN echo "nameserver ${NAME_SERVER}" >> /etc/resolv.conf \ 
    && wget https://github.com/eclipse/sumo/archive/v${SUMO_VERSION}.tar.gz \
    && mkdir /opt \
    && tar xzvf v${SUMO_VERSION}.tar.gz -C /opt \
    && rm v${SUMO_VERSION}.tar.gz 

RUN echo "nameserver ${NAME_SERVER}" >> /etc/resolv.conf \ 
    && apk add --no-cache g++ musl-dev make autoconf automake libtool 

# xerces 3.1.2
# taken from https://github.com/ojbc/docker/blob/master/apache-shib-sp-base/Dockerfile#L49
RUN wget http://archive.apache.org/dist/xerces/c/3/sources/xerces-c-3.1.2.tar.gz && \
	tar -xvf xerces-c-3.1.2.tar.gz && \
	cd xerces-c-3.1.2 && \
	./configure --prefix=/opt/shibboleth-sp --disable-netaccessor-libcurl && \
	make && \
	make install && \
	cd .. && rm -rf xerces-c*

RUN ln -s /opt/shibboleth-sp/lib/libxerces-c-3.1.so /usr/lib/libxerces-c.so \
    && ln -s /opt/shibboleth-sp/include/xercesc  /usr/include/xercesc

RUN cd /opt/sumo-${SUMO_VERSION} \
    && make -f Makefile.cvs \
    && ./configure  \
    && make \
    && make install \
    && cd ..

RUN mkdir /app

COPY test.py /app
COPY corridor.sumocfg /app
COPY input_additional.add.xml /app
COPY corridor /app/corridor


RUN ln -s /opt/shibboleth-sp/lib/libxerces-c-3.1.so /usr/lib/libxerces-c-3.1.so 

WORKDIR /app

ENV SUMO_HOME=/opt/sumo-${SUMO_VERSION}

ENTRYPOINT sumo --version \
    && python test.py

