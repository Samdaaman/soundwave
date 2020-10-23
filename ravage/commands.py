from dataclasses import dataclass

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
        process = subprocess.Popen([script_path] + self.script_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return f'out: "{out}"\nerr: "{err}"'


all_commands = [
    CommandHello('hello'),
    CommandGenericScript('linenum', 'LinEnum.sh', ['-t']),
    CommandGenericScript('linpeas', 'linpeas.sh', ['-a'])
]