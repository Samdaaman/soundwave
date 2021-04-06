import os
import sys
import subprocess

PROCESS_NAME = 'kworkerd'
DEBUG = True


layer = int(os.environ.get('LAYER', '0'))
os.environ['LAYER'] = str(layer + 1)

if layer == 0:
    child = subprocess.Popen(
        ['python3', 'entrypoint.py'],
        stdout=subprocess.PIPE
    )
    grand_child_pid = child.stdout.readline().decode()[:-1]
    print(f'Ravage: Running at {grand_child_pid}')

    if DEBUG:
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

    grand_child.stdin.write(f'exec -a {PROCESS_NAME} python3\n'.encode())
    grand_child.stdin.flush()
    with open(f'entrypoint.py', 'rb') as fh:
        grand_child.stdin.write(fh.read())
    grand_child.stdin.close()

    print(grand_child.pid, flush=True)
    if DEBUG:
        import time
        time.sleep(10)

else:
    sys.path.append(os.path.join(os.environ['RAVAGE_ROOT_DIR'], '..'))
    from ravage._private.start import start  # noqa
    start()
