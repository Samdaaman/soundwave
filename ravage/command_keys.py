from enum import Enum, auto


class COMMAND_KEYS(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    PING = auto()
    LINENUM = auto()
    LINPEAS = auto()
