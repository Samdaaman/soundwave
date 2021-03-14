import os
import libtmux
from typing import Optional, List
from queue import SimpleQueue
import threading
from enum import Enum
import socket


class TargetStatus(Enum):
    INITIALISED = 1
    CONNECTED = 2
    VERIFIED = 3
    ERROR = 4


class Target:
    name: str
    local_port: int
    remote_ip: str
    sock: socket.socket

    def __init__(self, name: str, remote_ip: str):
        self.name = name
        self.remote_ip = remote_ip
        self._status = TargetStatus.INITIALISED
        self._status_lock = threading.Lock()

        global last_used_port
        last_used_port_lock.acquire()
        try:
            while True:
                last_used_port += 1
                try:
                    self.sock = socket.create_server(('', last_used_port))
                    self.local_port = last_used_port
                    break
                except socket.error:
                    pass
        finally:
            last_used_port_lock.release()

    def set_status(self, status: TargetStatus):
        self._status_lock.acquire()
        self._status = status
        self._status_lock.release()

    def get_status(self) -> TargetStatus:
        self._status_lock.acquire()
        status = self._status
        self._status_lock.release()
        return status


tmux = None
soundwave_ip = '127.0.0.1'
target_ip = '127.0.0.1'
ADAPTER = 'lo'
RESULTS_DIR = 'results'
queue_commands = SimpleQueue()
queue_results = SimpleQueue()
targets = []  # type: List[Target]
last_used_port = 13369
last_used_port_lock = threading.Lock()


def set_soundwave_ip():
    global soundwave_ip
    result = ''.join(os.popen('ifconfig').readlines())
    result_arr = result.split(': flags')
    for i in range(len(result_arr) - 1):
        if i == 0:
            name = result_arr[i]
        else:
            name = result_arr[i].split('\n')[-1]

        try:
            ip = result_arr[i + 1].split('inet ')[1].split(' ')[0]

            if name == ADAPTER:
                soundwave_ip = ip
                print(f'Set Soundwave IP to {ip}')
                return
        except IndexError:
            pass

    print('Could not set Soundwave IP, check adapters')
    exit(-1)


def connect_to_tmux() -> Optional[str]:
    return # TODO
    global tmux
    try:
        sessions = libtmux.Server().list_sessions()
    except:
        return 'Tmux session not found, please start tmux first'

    if len(sessions) == 1:
        tmux = sessions[0]
        tmux.attached_window.rename_window('Soundwave')

        for window in tmux.windows:
            if window['window_name'].startswith('SW: '):
                window.kill_window()
    else:
        return 'More than one session found, please dev this bit'


set_soundwave_ip()
