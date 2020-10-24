from . import config
from . import commands
from typing import List
import base64
from time import sleep


def send_command_to_target(command: commands.Command, target: config.Target):
    command_parts = [command.command_key]  # type: List[str]
    data = b':'.join([base64.b64encode(command_part.encode('utf-8')) for command_part in command_parts]) + b'\n'
    target.sock.send(data)


def wait_for_results_from_target(target: config.Target):
    buffer = bytearray()
    while True:
        while True:
            chunk = target.sock.recv(1024)
            buffer.extend(chunk)
            if b'\n' in chunk:
                break
        result_raw = buffer.split(b'\n')[0]
        del buffer[0:buffer.find(b'\n') + 1]

        result_parts = [base64.b64decode(result_part).decode('utf-8') for result_part in result_raw.split(b':')]
        config.queue_results.put((target, result_parts))
