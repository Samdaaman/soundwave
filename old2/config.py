import os
from typing import List
from queue import SimpleQueue, Empty
import threading
from enum import Enum
import socket
import logging
import sys

from ravage.core import communication
from ravage.core.message import Message, MESSAGE_TYPES, MESSAGE_SOURCE_TYPES, ACTIONS

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


class TargetStatus(Enum):
    INITIALISED = 1
    CONNECTED = 2
    VERIFIED = 3
    ERROR = 4


class Target:
    name: str
    local_port: int
    remote_ip: str
    _messages_received: 'SimpleQueue[Message]'
    _messages_to_send: 'SimpleQueue[Message]'

    def __init__(self, name: str, remote_ip: str):
        self.name = name
        self.remote_ip = remote_ip
        # self._status = TargetStatus.INITIALISED
        # self._status_lock = threading.Lock()
        self._messages_to_send = SimpleQueue()
        self._messages_received = SimpleQueue()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        last_used_port_lock.acquire()

        def try_port():
            try:
                global last_used_port
                last_used_port += 1
                self.local_port = last_used_port
                sock.bind(('0.0.0.0', last_used_port))
                return True
            except:
                return False
        while try_port():
            pass
        last_used_port_lock.release()
        print(self.local_port)

        def do_work():
            sock.listen(1)
            communication.initialise_with_sock(sock.accept()[0], self._messages_to_send, self._messages_received)

            same_ip_targets = list(filter(lambda x: x.remote_ip == self.remote_ip, targets))
            if len(same_ip_targets) > 0:
                for target in same_ip_targets:
                    target.send_message(Message(
                        MESSAGE_SOURCE_TYPES.RAVAGE_CORE,
                        MESSAGE_TYPES.ACTION,
                        sub_type=ACTIONS.SHUTDOWN.value
                    ))

            targets.append(self)
            self.send_message(Message(
                MESSAGE_SOURCE_TYPES.SOUNDWAVE,
                MESSAGE_TYPES.ACTION,
                sub_type=ACTIONS.HELLO.value
            ))
            print(f'Target {remote_ip} created and connected')
        threading.Thread(target=do_work, daemon=True).start()

    def send_message(self, message: Message):
        self._messages_to_send.put(message)

    def get_received_message(self, block=True):
        if block:
            return self._messages_received.get()
        else:
            try:
                return self._messages_received.get_nowait()
            except Empty:
                return None

    # def set_status(self, status: TargetStatus):
    #     self._status_lock.acquire()
    #     self._status = status
    #     self._status_lock.release()
    #
    # def get_status(self) -> TargetStatus:
    #     self._status_lock.acquire()
    #     status = self._status
    #     self._status_lock.release()
    #     return status


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

#
# def connect_to_tmux() -> Optional[str]:
#     return  # TODO
#     global tmux
#     try:
#         sessions = libtmux.Server().list_sessions()
#     except:
#         return 'Tmux session not found, please start tmux first'
#
#     if len(sessions) == 1:
#         tmux = sessions[0]
#         tmux.attached_window.rename_window('Soundwave')
#
#         for window in tmux.windows:
#             if window['window_name'].startswith('SW: '):
#                 window.kill_window()
#     else:
#         return 'More than one session found, please dev this bit'
#

set_soundwave_ip()
