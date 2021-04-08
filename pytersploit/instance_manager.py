import my_logging
from typing import List, Optional, Tuple
from queue import Empty, SimpleQueue
from threading import Thread
from time import sleep

from pyterpreter import Message
from instance import Instance
from reply_handler import ReplyHandler

logger = my_logging.Logger('INSTANCE_MANAGER')


class InstanceManager:
    _instances: List[Instance] = []
    messages_to_send: 'SimpleQueue[Tuple[Instance, Message]]' = SimpleQueue()
    messages_sent: List[Tuple[Instance, Message]] = []
    messages_received: List[Tuple[Instance, Message]] = []

    @staticmethod
    def get_uids():
        return tuple(map(lambda x: x.uid, InstanceManager._instances))

    @staticmethod
    def get_all():
        return tuple(InstanceManager._instances)

    @staticmethod
    def get_by_uid(uid: Optional[str]) -> Optional[Instance]:
        if uid is None:
            return None
        filtered = tuple(filter(lambda x: x.uid == uid, InstanceManager._instances))
        return filtered[0] if len(filtered) == 1 else None

    @staticmethod
    def get_by_conversation_uid(uid: str):
        for instance, message in InstanceManager.messages_sent[::-1]:
            if message.conversation_uid == uid:
                return instance
        raise Exception('Could not find conversation')

    @staticmethod
    def try_add(instance: Instance):
        if not any([instance.ip == test.ip and instance.username == test.username for test in InstanceManager._instances]):
            instance.start_communication()
            InstanceManager._instances.append(instance)
            logger.info(f'Added instance {instance}')

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
                                ReplyHandler.handle_message_reply(instance, previous_message, message)
                                InstanceManager.messages_received.append((instance, message))
                                break
                        else:
                            raise Exception(f'Could not find previous message for reply: {message}')
                    else:
                        raise Exception(f'Unknown received message purpose: {message.purpose}')

    @staticmethod
    def start_worker(block=False):
        if block:
            while True:
                InstanceManager._worker_poll()
                sleep(0.5)
        else:
            Thread(target=InstanceManager.start_worker, args=(True,), daemon=True).start()
