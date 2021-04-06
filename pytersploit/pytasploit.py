import socket
import logging
from time import sleep

from pyterpreter import Core, Message
import web_server

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def main():
    logger.info('Starting web server')
    web_server.start()
    logger.info('Web server running')
    server = socket.create_server(('0.0.0.0', 1337))
    while True:
        sock, (ip, port) = server.accept()
        Core.initialise_communication(sock)
        logger.info(f'Communication initialised with {ip}:{port}')
        sleep(3)
        logger.info('Sending message')
        Core.messages_to_send.put(Message(
            Message.SCRIPT,
            '001',
            'test.sh'
        ))

        logger.info(f'Received message {Core.messages_received.get()}')


if __name__ == '__main__':
    main()