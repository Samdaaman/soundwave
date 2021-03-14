import config
import commands
import threading


def initialise():
    def process_results():
        print('Waiting for results')
        while True:
            result_parts = config.queue_results.get()
            print('Got a result')
            target = result_parts[0]
            command_key = result_parts[1][0]
            command_result = result_parts[1][1]

            def get_command():
                for command_loop in commands.all_commands:
                    if command_key == command_loop.key:
                        return command_loop
                raise NotImplementedError(f'Command result received is not implemented yet (for key {command_key})')

            command = get_command()
            command.process_result(command_result, target)

    threading.Thread(target=process_results, daemon=True).start()
