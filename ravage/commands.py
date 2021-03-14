import os
from typing import List, Union
import subprocess

from .command_keys import COMMAND_KEYS

SCRIPTS_DIR = f'resources/scripts'


class Command:
    key: str

    def __init__(self, key: Union[str, COMMAND_KEYS]):
        if isinstance(key, COMMAND_KEYS):
            self.key = key.value
        else:
            self.key = key

    def get_result(self) -> str:
        raise NotImplementedError('Running of command has not been implemented yet')


class CommandPing(Command):
    def get_result(self) -> str:
        return 'Hello from Ravage'


class CommandGenericScript(Command):
    script_name: str
    script_args: List[str]

    def __init__(self, key: Union[str, COMMAND_KEYS], script_name: str, script_args: List[str]):
        self.script_name = script_name
        self.script_args = script_args
        super(CommandGenericScript, self).__init__(key)

    def get_result(self) -> str:
        script_path = f'{SCRIPTS_DIR}/{self.script_name}'
        os.system(f'chmod +x {script_path}')
        process = subprocess.Popen([script_path] + self.script_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out.decode("utf-8")


def assert_has_all_commands(commands: List[Command]):
    for command_key in COMMAND_KEYS:
        for command in commands:
            if command.key == command_key.value:
                break
        else:
            raise Exception(f'Command for key {command_key.value} missing')


all_commands = [
    CommandPing(COMMAND_KEYS.PING),
    CommandGenericScript(COMMAND_KEYS.LINENUM, 'LinEnum.sh', ['-t']),
    CommandGenericScript(COMMAND_KEYS.LINPEAS, 'linpeas.sh', ['-a'])
]



