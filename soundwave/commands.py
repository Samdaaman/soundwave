from . import config
from dataclasses import dataclass


@dataclass
class Command:
    command_key: str

    def before(self):
        pass

    def process_result(self, result: str, target: config.Target):
        raise NotImplementedError()


class CommandHello(Command):
    def process_result(self, result: str, target: config.Target):
        if result == 'Hello from Ravage':
            target.set_status(config.TargetStatus.VERIFIED)


@dataclass
class CommandGenericScript(Command):
    command_key: str

    def process_result(self, result: str, target: config.Target):
        with open(f'{config.RESULTS_DIR}/{target.name}_{self.command_key}.out.txt', 'w') as fh:
            fh.write(result)


all_commands = [
    CommandHello('hello'),
    CommandGenericScript('linenum'),
    CommandGenericScript('linpeas')
]

