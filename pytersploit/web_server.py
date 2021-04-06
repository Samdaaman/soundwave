import http.server
import os
from threading import Thread
import subprocess
from time import sleep


PORT = 1338


def start():
    Thread(target=_start, daemon=True).start()
    while True:
        ping = subprocess.run(f'curl -s http://localhost:{PORT}', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        if ping.returncode == 0:
            return
        else:
            sleep(0.5)


def _start():
    http.server.ThreadingHTTPServer(
        ('0.0.0.0', PORT),
        RequestHandler
    ).serve_forever()


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(directory=os.path.join(os.getcwd(), 'resources'), *args, **kwargs)

    def log_message(self, *args) -> None:
        pass
