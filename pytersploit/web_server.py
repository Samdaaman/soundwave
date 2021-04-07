import http.server
import os
from threading import Thread
import subprocess
from time import sleep


PORT = 1338


def get_available_scripts():
    scripts = []
    for file in os.listdir(os.path.join('resources', 'scripts')):
        path = os.path.join('resources', 'scripts', file)
        if os.path.isfile(path):
            scripts.append(path)
    return scripts


def start(block=False, wait=True):
    if block:
        http.server.ThreadingHTTPServer(
            ('0.0.0.0', PORT),
            RequestHandler
        ).serve_forever()
    else:
        Thread(target=start, args=(True,), daemon=True).start()
        if wait:
            while True:
                ping = subprocess.run(f'curl -s http://localhost:{PORT}', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                if ping.returncode == 0:
                    return
                else:
                    sleep(0.5)


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(directory=os.path.join(os.getcwd(), 'resources'), *args, **kwargs)

    def log_message(self, *args) -> None:
        pass
