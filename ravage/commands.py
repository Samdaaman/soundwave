from dataclasses import dataclass
import os
from typing import List
import subprocess
from command_keys import COMMAND_KEYS

SCRIPTS_DIR = f'resources/scripts'


@dataclass
class Command:
    command_key: COMMAND_KEYS

    def get_result(self) -> str:
        raise NotImplementedError('Running of command has not been implemented yet')


class CommandPing(Command):
    def get_result(self) -> str:
        return 'Hello from Ravage'


@dataclass
class CommandGenericScript(Command):
    script_name: str
    script_args: List[str]

    def get_result(self) -> str:
        script_path = f'{SCRIPTS_DIR}/{self.script_name}'
        os.system(f'chmod +x {script_path}')
        process = subprocess.Popen([script_path] + self.script_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out.decode("utf-8")


all_commands = [
    CommandPing(COMMAND_KEYS.PING),
    CommandGenericScript(COMMAND_KEYS.LINENUM, 'LinEnum.sh', ['-t']),
    CommandGenericScript(COMMAND_KEYS.LINPEAS, 'linpeas.sh', ['-a'])
]