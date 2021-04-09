from ubuntu

RUN apt-get update
RUN apt-get install -y net-tools python3 curl

# RUN echo '127.0.0.1 mint' >> /etc/hosts
# RUN echo 'bob ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
RUN useradd -m -s /bin/bash bob

RUN echo "root: " | chpasswd

COPY pyterpreter.py /pyterpreter.py

ENTRYPOINT su -l bob