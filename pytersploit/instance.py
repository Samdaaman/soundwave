import socket
import datetime
from queue import SimpleQueue
from threading import Thread
import my_logging

from pyterpreter import Core, Message

logger = my_logging.Logger('INSTANCE')


class Instance:
    uid: str
    ip: str
    port: int
    sock: socket.socket
    username: str
    last_message: int
    message_received_queue: 'SimpleQueue[Message]'
    message_to_send_queue: 'SimpleQueue[Message]'
    _sender_thread: Thread
    _receiver_thread: Thread

    def __init__(self, ip: str, port: int, sock: socket.socket, username: str):
        self.uid = f'{username}:{ip}:{port}'
        self.ip = ip
        self.port = port
        self.sock = sock
        self.username = username
        self.last_message = int(datetime.datetime.now().timestamp())
        self.message_received_queue = SimpleQueue()  # type: SimpleQueue[Message]
        self.message_to_send_queue = SimpleQueue()  # type: SimpleQueue[Message]
        self._receiver_thread = Thread(target=self._receive_messages_forever, daemon=True)

    def __str__(self):
        return f'{self.username}@{self.ip}'

    @property
    def is_root(self):
        return self.username == 'root'

    @property
    def active(self):
        return True

    def start_communication(self):
        self._receiver_thread.start()

    def _receive_messages_forever(self):
        while True:
            self.message_received_queue.put(Message.from_raw(Core.receive_line_from_sock(self.sock)))

    def _send_messages_forever(self):
        while True:
            self.sock.send(self.message_to_send_queue.get().to_raw() + b'\n')
