import subprocess
import sys

PORT = '7890'


def main():
    print('Initialising Communications on port:' + PORT)
    process = subprocess.Popen(["nc", "-lvp", PORT], stdout=subprocess.PIPE, universal_newlines=True)
    while process.stdout.readline() != 'Listening on [0.0.0.0] (family 0, port ' + PORT + ')':
        if process.poll() is not None:
            raise Exception('Unexpected Error 101')
    print('Connection from Host received')
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        print('line = ' + line)

    output = process.communicate()[0]
    print('ouput = ' + output)
    exitcode = process.returncode
    print('exitcode = ' + str(exitcode))


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or above required")
    main()
