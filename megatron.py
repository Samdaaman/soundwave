import subprocess
import sys

PORT = '7890'

def main():
    print('Initialising Communications on port:' + PORT)
    process = subprocess.Popen(["nc", "-lvp", PORT], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    while 'received!' not in process.stderr.readline():
        if process.poll() is not None:
            raise Exception('Unexpected Error 101 - nc closed unexpectedly')
    print('Connection from soundwave received')
    while True:
        command = input('Command or Enter to Refresh:\n')
        if command != '':
            process.stdin.write('-bc\n')
            process.stdin.flush()
            process.stdin.write(command + '\n')
            process.stdin.flush()
            reply = ''
            while True:
                reply = process.stdout.readline().rstrip()
                if reply == '-ec':
                    break
                print(reply)

        if process.poll() is not None:
            print('Process terminated on soundwave end')
            break


    output = process.communicate()[0]
    print('ouput = ' + output)
    exitcode = process.returncode
    print('exitcode = ' + str(exitcode))


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or above required")
    main()
