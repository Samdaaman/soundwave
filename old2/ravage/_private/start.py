import os

from . import config


def start():
    config.SOUNDWAVE_IP = os.environ['SOUNDWAVE_IP']
    config.RAVAGE_IP = os.environ['RAVAGE_IP']
    config.COMMUNICATION_PORT = int(os.environ['COMMUNICATION_PORT'])
    config.RAVAGE_ROOT_DIR = os.environ['RAVAGE_ROOT_DIR']

    config.initialise_communication()

    config.log('Ravage Initialised')

    while True:
        pass
