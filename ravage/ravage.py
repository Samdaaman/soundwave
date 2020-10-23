import os
import sys
from time import sleep
import settings

if len(sys.argv) != 3:
    raise Exception('Called with wrong amount of arguments')
else:
    settings.ravage_ip = sys.argv[1]
    settings.soundwave_ip = sys.argv[2]

os.system(f'cat hello.txt | nc {settings.soundwave_ip} 1338')

print('Dying after 10 seconds')
sleep(10)
