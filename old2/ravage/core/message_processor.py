from queue import SimpleQueue
from threading import Thread
import abc

from .communication import Message


class MessageProcessorBase(abc.ABC):
    def __init__(self, messages_received: 'SimpleQueue[Message]', messages_to_send: 'SimpleQueue[Message]'):
        self._messages_to_send = messages_to_send

        def do_work():
            while True:
                try:
                    message = messages_received.get()
                    self.on_message(message)

                except Exception as ex:
                    self.on_exception(ex)
        Thread(target=do_work, daemon=True).start()

    def send_message(self, message: Message):
        self._messages_to_send.put(message)

    @abc.abstractmethod
    def on_exception(self, ex: Exception):
        pass

    @abc.abstractmethod
    def on_message(self, message: Message):
        pass
