import subprocess
import sys

PORT_MAIN = '7890'
PORT_SHELL = '7891'


def main():
    print('Initialising Communications on port:' + PORT_MAIN)
    process_main = subprocess.Popen(["nc", "-lvp", PORT_MAIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    while 'received!' not in process_main.stderr.readline():
        if process_main.poll() is not None:
            raise Exception('Unexpected Error 101 - nc (main) closed unexpectedly')

    print('Initialising Shell on port:' + PORT_SHELL)
    process_shell = subprocess.Popen(["gnome-terminal", "--", "nc", "-lvp", PORT_SHELL], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


    print('Connection from soundwave received')
    while True:
        check_file_update()

        if process_main.poll() is not None:
            print('Process terminated on soundwave end')
            break


    output = process_main.communicate()[0]
    print('ouput = ' + output)
    exitcode = process_main.returncode
    print('exitcode = ' + str(exitcode))


def check_file_update():
    return


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or above required")
    main()