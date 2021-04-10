import http.server
import os
from threading import Thread
import subprocess
from time import sleep

from my_logging import Logger

logger = Logger('WEB_SERVER')
PORT = 1338


def get_available_scripts():
    scripts = []
    for file in os.listdir(os.path.join('../resources', 'scripts')):
        path = os.path.join('resources', 'scripts', file)
        if os.path.isfile(path):
            scripts.append(path)
    return scripts


def start(block=False, should_wait=True):
    if block:
        logger.debug('Starting...')
        http.server.ThreadingHTTPServer(
            ('0.0.0.0', PORT),
            RequestHandler
        ).serve_forever()
    else:
        Thread(target=start, args=(True,), daemon=True).start()

        def wait():
            while True:
                ping = subprocess.run(f'curl -s http://localhost:{PORT}', shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                if ping.returncode == 0:
                    logger.info('Started Web Server')
                    return
                else:
                    sleep(0.5)

        if should_wait:
            wait()
        else:
            Thread(target=wait, daemon=True).start()


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(directory=os.path.join(os.getcwd(), '../resources'), *args, **kwargs)

    def log_message(self, *args) -> None:
        pass
