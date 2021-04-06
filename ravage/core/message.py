import base64
from enum import auto, Enum
from typing import Optional


class MESSAGE_SOURCE_TYPES(Enum):
    def _generate_next_value_(name, start, count, last_values):  # noqa
        return name

    SOUNDWAVE = auto()
    RAVAGE_CORE = auto()
    RAVAGE_WORKER = auto()


class MESSAGE_TYPES(Enum):
    def _generate_next_value_(name, start, count, last_values):  # noqa
        return name

    ACTION = auto()
    ACTION_RESULT = auto()
    LOG_DEBUG = auto()
    LOG_ERROR = auto()


class ACTIONS(Enum):
    def _generate_next_value_(name, start, count, last_values):  # noqa
        return name

    HELLO = auto()
    SHUTDOWN = auto()


class Message:
    source_type: MESSAGE_SOURCE_TYPES
    type: MESSAGE_TYPES
    source_id: str
    sub_type: str
    data: str

    def __init__(self, source_type: MESSAGE_SOURCE_TYPES, type: MESSAGE_TYPES, source_id: Optional[str] = None, sub_type: Optional[str] = None, data: Optional[str] = None):
        self.source_type = source_type
        self.type = type
        self.source_id = source_id if source_id is not None else ''
        self.sub_type = sub_type if sub_type is not None else ''
        self.data = data if data is not None else ''

    def __str__(self):
        return f'{self.source_type.value}:{self.type.value}:{self.source_id}:{self.sub_type}:{len(self.data)}'

    @classmethod
    def from_line(cls, line: bytes) -> 'Message':
        line_parts = [base64.b64decode(line_part).decode('utf-8') for line_part in line.split(b':')]
        return Message(
            MESSAGE_SOURCE_TYPES[line_parts[0]],
            MESSAGE_TYPES[line_parts[1]],
            line_parts[2],
            line_parts[3],
            line_parts[4]
        )

    def to_line(self) -> bytes:
        return b':'.join([base64.b64encode(line_part.encode()) for line_part in [
            self.source_type.value,
            self.type.value,
            self.source_id,
            self.sub_type,
            self.data
        ]]) + b'\n'
