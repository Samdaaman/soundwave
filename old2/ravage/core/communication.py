import threading
import socket
from queue import SimpleQueue

from .message import Message


def initialise(ip: str, port: int, messages_to_send: 'SimpleQueue[Message]', messages_received: 'SimpleQueue[Message]'):
    sock = socket.create_connection((ip, port))
    initialise_with_sock(sock, messages_to_send, messages_received)


def initialise_with_sock(sock: socket.socket, messages_to_send: 'SimpleQueue[Message]', messages_received: 'SimpleQueue[Message]'):
    def sender():
        while True:
            message_raw = messages_to_send.get().to_line()
            sock.send(message_raw)

    def receiver():
        buffer = bytearray()
        while True:
            while True:
                chunk = sock.recv(1)
                buffer.extend(chunk)
                if b'\n' == chunk:
                    break

            message = Message.from_line(buffer)
            messages_received.put(message)

    threading.Thread(target=sender, daemon=True).start()
    threading.Thread(target=receiver, daemon=True).start()
