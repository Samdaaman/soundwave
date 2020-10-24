from dataclasses import dataclass
import os
from typing import List
import subprocess

RESOURCES_DIR = 'resources'


@dataclass
class Command:
    command_key: str

    def get_result(self) -> str:
        raise NotImplementedError('Running of command has not been implemented yet')


class CommandHello(Command):
    def get_result(self) -> str:
        return 'Hello from Ravage'


@dataclass
class CommandGenericScript(Command):
    command_key: str
    script_name: str
    script_args: List[str]

    def get_result(self) -> str:
        script_path = f'{RESOURCES_DIR}/{self.script_name}'
        os.system(f'chmod +x {script_path}')
        process = subprocess.Popen([script_path] + self.script_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out.decode("utf-8")


all_commands = [
    CommandHello('hello'),
    CommandGenericScript('linenum', 'LinEnum.sh', ['-t']),
    CommandGenericScript('linpeas', 'linpeas.sh', ['-a'])
]