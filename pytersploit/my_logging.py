from typing import Callable


def set_output_func(output_func: Callable[[str], None]):
    Logger.output_func = output_func


class Logger:
    name: str
    output_func: Callable[[str], None]

    def __init__(self, name: str):
        self.name = name

    def _print(self, line: str):
        Logger.output_func(f'[{self.name}] {line}')

    def info(self, line: str):
        self._print(line)

    def debug(self, line: str):
        self._print(line)
