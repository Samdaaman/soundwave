from . import config
from . import commands
import threading


def process_results():
    result_parts = config.queue_results.get()
    target = result_parts[0]
    command_key = result_parts[1][0]
    command_result = result_parts[1][1]

    def get_command():
        for command_loop in commands.all_commands:
            if command_key == command_loop.command_key:
                return command_loop
        raise NotImplementedError(f'Command result received is not implemented yet (for key {command_key})')

    command = get_command()
    command.process_result(command_result, target)


def initialise():
    threading.Thread(target=process_results)
