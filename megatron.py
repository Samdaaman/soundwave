import subprocess
import sys

PORT_MAIN = '7890'
PORT_SHELL = '7891'


def main():
    print('Initialising Communications on port:' + PORT_MAIN)
    process_main = subprocess.Popen(["nc", "-lvp", PORT_MAIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while 'received!' not in process_main.stderr.readline():
        if process_main.poll() is not None:
            raise Exception('Unexpected Error 101 - nc (main) closed unexpectedly')

    print('Initialising Shell on port:' + PORT_SHELL)
    process_shell = subprocess.Popen(["gnome-terminal", "-e", "nc", "-lvp", PORT_SHELL], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while 'received!' not in process_shell.stderr.readline():
        if process_shell.poll() is not None:
            raise Exception('Unexpected Error 102 - nc (shell) closed unexpectedly')

    print('Connection from soundwave received')
    while True:
        command = input('Input Command or Enter to Refresh:\n')
        if command != '':
            process_main.stdin.write('-bc\n')
            process_main.stdin.flush()
            process_main.stdin.write(command + '\n')
            process_main.stdin.flush()
            reply = ''
            while True:
                reply = process_main.stdout.readline().rstrip()
                if reply == '-ec':
                    break
                print(reply)

        if process_main.poll() is not None:
            print('Process terminated on soundwave end')
            break


    output = process_main.communicate()[0]
    print('ouput = ' + output)
    exitcode = process_main.returncode
    print('exitcode = ' + str(exitcode))


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or above required")
    main()
