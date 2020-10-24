import sys
from time import sleep
import config
import commands
import communication

if len(sys.argv) != 4:
    raise Exception('Called with wrong amount of arguments')
else:
    config.ravage_ip = sys.argv[1]
    config.soundwave_ip = sys.argv[2]
    config.communication_port = int(sys.argv[3])

print('Ravage initialised and trying to connect back to Soundwave')

communication.connect()
print('Successfully connected to Soundwave')
communication.process_commands_forever()
communication.listen_for_commands_forever()


while True:
    pass
