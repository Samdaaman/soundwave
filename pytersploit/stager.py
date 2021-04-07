import socket
import logging
from threading import Thread
from typing import Tuple
from base64 import b64decode

from pyterpreter import Core
from instance import Instance
from instance_manager import InstanceManager

logger = logging.Logger('STAGER')


def _handler(sock: socket.socket, address: Tuple[str, int]):
    logger.debug(f'Connected on {address[0]}:{address[1]}')
    header = Core.receive_line_from_sock(sock)
    header_parts = [b64decode(header_part).decode() for header_part in header.split(b':')]
    InstanceManager.try_add(Instance(address[0], address[1], sock, header_parts[0]))


def initialise(block=False):
    if block:
        logger.info('Starting server')
        server = socket.create_server(('', 1337))
        while True:
            sock, address = server.accept()
            Thread(target=_handler, args=(sock, address), daemon=True).start()
    else:
        Thread(target=initialise, args=(True,), daemon=True).start()

