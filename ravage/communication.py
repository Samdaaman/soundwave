import threading
import socket
from typing import Optional
import base64

from . import config
from . import commands

sock = None  # type: Optional[socket.socket]


def process_commands_forever():
    def do_work():
        while True:
            command = config.queue_commands.get()  # type: commands.Command
            result = command.get_result()
            data = b':'.join([base64.b64encode(data_part.encode('utf-8')) for data_part in [command.key, result]]) + b'\n'
            sock.send(data)

    threading.Thread(target=do_work, daemon=True).start()


def listen_for_commands_forever():
    buffer = bytearray()
    while True:
        while True:
            chunk = sock.recv(1024)
            buffer.extend(chunk)
            if b'\n' in chunk:
                break
        command_raw = buffer.split(b'\n')[0]
        del buffer[0:buffer.find(b'\n') + 1]

        command_parts = [base64.b64decode(command_part).decode('utf-8') for command_part in command_raw.split(b':')]
        command_key = command_parts[0]

        for command in commands.all_commands:
            if command.key == command_key:
                config.queue_commands.put(command)
                break
        else:
            raise Exception(f'Command not found for command_key: "{command_key}"')


def connect():
    global sock
    sock = socket.create_connection((config.SOUNDWAVE_IP, config.COMMUNICATION_PORT))
