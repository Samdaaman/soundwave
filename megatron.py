import subprocess
import sys

PORT = '7890'


def main():
    print('Initialising Communications on port:' + PORT)
    popen = subprocess.Popen("nc", stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline(), ""):
        print(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or above required")
    main()
