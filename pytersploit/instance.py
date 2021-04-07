from typing import List, Tuple
import socket
import datetime
from queue import Empty, SimpleQueue
from threading import Thread
from time import sleep
import logging

from pyterpreter import Core, Message

logger = logging.getLogger()


class Instance:
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
        self.ip = ip
        self.port = port
        self.sock = sock
        self.username = username
        self.last_message = int(datetime.datetime.now().timestamp())
        self.message_received_queue = SimpleQueue()  # type: SimpleQueue[Message]
        self.message_to_send_queue = SimpleQueue()  # type: SimpleQueue[Message]
        self._receiver_thread = Thread(target=self._receive_messages_forever, daemon=True)

    def __repr__(self):
        return f'{self.username} [{self.ip}]'

    @property
    def is_root(self):
        return self.username == 'root'

    def start_communication(self):
        self._receiver_thread.start()

    def _receive_messages_forever(self):
        while True:
            self.message_received_queue.put(Message.from_raw(Core.receive_line_from_sock(self.sock).decode()))

    def _send_messages_forever(self):
        while True:
            self.sock.send(self.message_to_send_queue.get().to_raw() + b'\n')


class InstanceManager:
    _instances: List[Instance] = []
    messages_to_send: 'SimpleQueue[Tuple[Instance, Message]]' = SimpleQueue()
    messages_sent: List[Tuple[Instance, Message]] = []
    messages_received: List[Tuple[Instance, Message]] = []

    @staticmethod
    def try_add(instance: Instance):
        if not any([instance.ip == test.ip and instance.username == test.username for test in InstanceManager._instances]):
            instance.start_communication()
            InstanceManager._instances.append(instance)
            logger.info(f'Added instance {instance}')

    @staticmethod
    def _worker_poll():
        # Send any messages
        while True:
            try:
                instance, message = InstanceManager.messages_to_send.get_nowait()
            except Empty:
                break
            else:
                instance.sock.send(message.to_raw() + b'\n')
                InstanceManager.messages_sent.append((instance, message))

        # Process and collate replies
        for instance in InstanceManager._instances:
            while True:
                try:
                    message = instance.message_received_queue.get_nowait()
                except Empty:
                    break
                else:
                    if message.purpose == message.REPLY:
                        for previous_instance, previous_message in InstanceManager.messages_sent[::-1]:
                            if previous_instance == instance and previous_message.conversation_uid == message.conversation_uid:
                                InstanceManager._process_message_reply(instance, previous_message, message)
                                InstanceManager.messages_received.append((instance, message))
                                break
                        else:
                            raise Exception(f'Could not find previous message for reply: {message}')
                    else:
                        raise Exception(f'Unknown received message purpose: {message.purpose}')

    @staticmethod
    def _process_message_reply(instance: Instance, message: Message, reply: Message):
        logger.info(f'Received reply from {instance}\n{reply}')

    @staticmethod
    def start_worker(block=False):
        if block:
            while True:
                InstanceManager._worker_poll()
                sleep(0.5)
        else:
            Thread(target=InstanceManager.start_worker, args=(True,), daemon=True)
