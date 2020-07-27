FROM python:3.7.1-alpine3.7

ARG name_server=192.168.43.1

ENV NAME_SERVER=$name_server

#RUN mkdir -p /app

COPY requirements.txt .

# gcc is needed to install a dependency of Faust.
# musl-dev is needed to solve the error:
# alpine fatal error: limits.h: No such file or directory
# while compiling a C dependency when installing Faust.

RUN echo "nameserver ${NAME_SERVER}" >> /etc/resolv.conf \ 
    && apk add --no-cache gcc musl-dev \
    && pip install -r requirements.txt

#WORKDIR /app

ENTRYPOINT python -c 'import faust; print(faust.__version__)'
