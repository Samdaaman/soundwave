import config
from dataclasses import dataclass
from ravage.command_keys import COMMAND_KEYS


@dataclass
class Command:
    command_key: COMMAND_KEYS

    def before(self):
        pass

    def process_result(self, result: str, target: config.Target):
        raise NotImplementedError()


class CommandPing(Command):
    def process_result(self, result: str, target: config.Target):
        if result == 'Hello from Ravage':
            target.set_status(config.TargetStatus.VERIFIED)
            print(f'Target {target.name}:{target.local_port} said hello', flush=True)


@dataclass
class CommandGenericScript(Command):
    def process_result(self, result: str, target: config.Target):
        with open(f'{config.RESULTS_DIR}/{target.name}_{self.command_key.value}.out.txt', 'w') as fh:
            fh.write(result)


all_commands = [
    CommandPing(COMMAND_KEYS.PING),
    CommandGenericScript(COMMAND_KEYS.LINENUM),
    CommandGenericScript(COMMAND_KEYS.LINPEAS)
]

