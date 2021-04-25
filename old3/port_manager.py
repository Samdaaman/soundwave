import socket
from threading import Lock
import errno


class PortManager:
    _last_used_port = 50000
    _lock = Lock()

    @staticmethod
    def get_open_port():
        PortManager._lock.acquire()
        try:
            while True:
                PortManager._last_used_port += 1
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.bind(('localhost', PortManager._last_used_port))
                    s.close()
                    return PortManager._last_used_port
                except socket.error as e:
                    if e.errno == errno.EADDRINUSE:
                        pass
                    else:
                        pass
        finally:
            PortManager._lock.release()
