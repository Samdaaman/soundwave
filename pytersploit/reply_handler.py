import socket
import subprocess
import tempfile
from select import select
from threading import Thread
import os

from instance import Instance
from pyterpreter import Message
import my_logging
from tmux import Tmux

logger = my_logging.Logger('REPLY_MANAGER')


class ReplyHandler:
    @staticmethod
    def handle_message_reply(instance: Instance, message: Message, reply: Message):
        logger.info(f'Received reply from {instance}\n{reply}')

    @staticmethod
    def handle_open_shell(instance: Instance, shell_sock: socket.socket):
        shell_stdin_filename = tempfile.mktemp()
        shell_stdout_filename = tempfile.mktemp()
        os.path.exists(shell_stdin_filename) and os.unlink(shell_stdin_filename)
        os.path.exists(shell_stdout_filename) and os.unlink(shell_stdout_filename)
        os.mkfifo(shell_stdin_filename)
        os.mkfifo(shell_stdout_filename)
        subprocess.run(f'tmux new-window -n {instance.username}@{instance.ip} {os.path.join(os.path.dirname(__file__), "shell", "shell")} {shell_stdin_filename} {shell_stdout_filename}', shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shell_stdin = open(shell_stdin_filename, 'wb', 0)
        shell_stdout = open(shell_stdout_filename, 'rb', 0)

        def clean_up():
            try:
                os.unlink(shell_stdin_filename)
            except:
                pass
            try:
                os.unlink(shell_stdout_filename)
            except:
                pass

        def reader():
            while True:
                buffer = shell_stdout.read(1)
                if buffer == b'':
                    break
                else:
                    shell_sock.send(buffer)
            clean_up()

        def writer():
            while True:
                buffer = shell_sock.recv(1)
                if buffer == b'':
                    break
                else:
                    shell_stdin.write(buffer)
            clean_up()

        Thread(target=reader, daemon=True).start()
        Thread(target=writer, daemon=True).start()
