import subprocess
import sys
import os
import base64

PORT_MAIN = '7890'
PORT_SHELL = '7891'

CMD_EXIT = '-e'
CMD_NEW_FILE = '-c'
CMD_END_FILE = '-t'
## TODO CMD_RM_FILE = '-r'
## TODO CMD_NEW_SHELL = '-s'

IGNORE_PREFIX = 'sndwv_'

SOUNDWAVE_NAME = 'soundwave.py'
MEGATRON_NAME = 'megatron.py'

processed_files = [MEGATRON_NAME, SOUNDWAVE_NAME]


def main():
    print('Initialising Communications on port:' + PORT_MAIN)
    process_main = subprocess.Popen(["nc", "-lvp", PORT_MAIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True)
    while 'received!' not in process_main.stderr.readline():
        if process_main.poll() is not None:
            raise Exception('Unexpected Error 101 - nc (main) closed unexpectedly')

    print('Initialising Shell on port:' + PORT_SHELL)
    process_shell = subprocess.Popen(["gnome-terminal", "--", "nc", "-lvp", PORT_SHELL], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    print('Connection from soundwave received')
    while True:
        files_update(process_main)

        if process_main.poll() is not None:
            print('Process terminated on soundwave end')
            break

    output = process_main.communicate()[0]
    print('ouput = ' + output)
    exitcode = process_main.returncode
    print('exitcode = ' + str(exitcode))


def files_update(process_main):
    # TODO add in file updates
    files_to_process = [f for f in os.listdir('.') if
                        os.path.isfile(f) and f not in processed_files and not f.startswith(IGNORE_PREFIX)]
    if not files_to_process:
        return

    for file_name in files_to_process:
        processed_files.append(file_name)
        transfer_file(file_name, process_main)


def transfer_file(file_name, process_main):
    print('Transferring file: ' + file_name)
    with open(file_name, 'rb') as file_handle:
        file_contents = file_handle.read()
    encoded = base64.b64encode(file_contents).decode('utf-8')
    stdin_writeline(CMD_NEW_FILE, process_main)
    stdin_writeline(file_name, process_main)
    stdin_writeline(encoded, process_main)
    stdin_writeline(CMD_END_FILE, process_main)


def stdin_writeline(line, process):
    process.stdin.write(line + '\n')
    process.stdin.flush()


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or above required")
    main()