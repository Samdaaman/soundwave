from queue import SimpleQueue
import sys

from .message_processor import MessageProcessor
from ..core.message import Message, MESSAGE_SOURCE_TYPES, MESSAGE_TYPES
from ..core import communication

SOUNDWAVE_IP: str
RAVAGE_IP: str
COMMUNICATION_PORT: int
RAVAGE_ROOT_DIR: str
DEBUG = True

_messages_to_send: 'SimpleQueue[Message]' = SimpleQueue()
_messages_received: 'SimpleQueue[Message]' = SimpleQueue()


def initialise_communication():
    communication.initialise(
        SOUNDWAVE_IP,
        COMMUNICATION_PORT,
        _messages_to_send,
        _messages_received,
    )
    MessageProcessor(_messages_received, _messages_to_send)


def log(message: str, source_id='', error=False):
    print(message, file=sys.stderr)
    if source_id != '':
        source_type = MESSAGE_SOURCE_TYPES.RAVAGE_WORKER
    else:
        source_type = MESSAGE_SOURCE_TYPES.RAVAGE_CORE

    _messages_to_send.put(Message(
        source_type,
        MESSAGE_TYPES.LOG_DEBUG if not error else MESSAGE_TYPES.LOG_ERROR,
        source_id,
        '',
        message
    ))
