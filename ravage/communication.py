import threading
from . import config
import socket
from .commands import Command
from typing import Optional
import base64

sock = None  # type: Optional[socket.socket]


def process_commands_forever():
    def do_work():
        while True:
            command = config.queue_commands.get()  # type: Command
            result = command.get_result()
            data = b':'.join([base64.encodebytes(data_part) for data_part in [command.command_key, result]])
            sock.send(data)

    threading.Thread(target=do_work)


def listen_for_commands_forever():
    pass  # TODO


def connect():
    global sock
    sock = socket.create_connection((config.soundwave_ip, config.communication_port))
