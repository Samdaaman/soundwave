# from enum import Enum
#
# class ResultType(Enum):
#     NONE = 1
#     RAW_WITH_OUTFILE = 2
#     STRING = 3

from typing import List
import subprocess

RESOURCES_DIR = 'resources'


class Command:
    def __init__(self, command_key: str):
        self.command_key = command_key

    def get_result(self) -> str:
        raise NotImplementedError('Running of command has not been implemented yet')

    def handle_result(self, result: str) -> None:
        raise NotImplementedError('Running of command has not been implemented yet')


class RawScriptCommand(Command):
    def __init__(self, command_key: str, script_name: str, script_args: List[str]):
        self.script_name = script_name
        self.script_args = script_args
        super(RawScriptCommand, self).__init__(command_key)

    def get_result(self) -> str:
        script_path = f'{RESOURCES_DIR}/{self.script_name}'
        process = subprocess.Popen([script_path] + self.script_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return f'out: "{out}"\nerr: "{err}"'

    def handle_result(self, result: str) -> None:
        with open(f'{self.script_name}.log.txt', 'w') as fh:
            fh.write(result)


command_linenum = RawScriptCommand('linenum', 'LinEnum.sh', ['-t'])
command_linpeas = RawScriptCommand('linpeas', 'linpeas.sh', ['-a'])

all_commands = [
    command_linenum,
    command_linpeas
]