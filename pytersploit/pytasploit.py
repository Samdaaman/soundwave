import logging

import stager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def main():
    logger.info('Starting server')
    stager.initialise(True)

    # while True:
    #     sock, (ip, port) = server.accept()
    #     Core.initialise_communication(sock)
    #     logger.info(f'Communication initialised with {ip}:{port}')
    #     sleep(3)
    #     logger.info('Sending message')
    #     Core.messages_to_send.put(Message(
    #         Message.SCRIPT,
    #         '001',
    #         'test.sh'
    #     ))
    #
    #     logger.info(f'Received message {Core.messages_received.get()}')


if __name__ == '__main__':
    main()