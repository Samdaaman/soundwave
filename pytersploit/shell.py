import sys
import os
from io import TextIOWrapper
from threading import Thread


def main():
    assert len(sys.argv) == 3
    in_file = open(sys.argv[1], 'rb', buffering=0)
    out_file = open(sys.argv[2], 'wb', buffering=0)

    def die():
        in_file.close()
        out_file.close()
        exit()

    def writer():
        try:
            while True:
                c = os.read(sys.stdin.fileno(), 1)
                out_file.write(c)
        except:
            die()

    def reader():
        try:
            while True:
                c = os.read(in_file.fileno(), 1)
                sys.stdout.write(c.decode())
        except:
            die()

    Thread(target=writer, daemon=True).start()
    reader()


if __name__ == '__main__':
    main()
