import config
from ravage.constants import COMMAND_KEYS
from typing import Union


class Command:
    key: str

    def __init__(self, key: Union[str, COMMAND_KEYS]):
        if isinstance(key, COMMAND_KEYS):
            self.key = str(key.value)
        else:
            self.key = str(key)

    def before(self):
        pass

    def process_result(self, result: str, target: config.Target):
        raise NotImplementedError()


class CommandPing(Command):
    def process_result(self, result: str, target: config.Target):
        if result == 'Hello from Ravage':
            target.set_status(config.TargetStatus.VERIFIED)
            print(f'Target {target.name}:{target.local_port} said hello', flush=True)


class CommandGenericScript(Command):
    def process_result(self, result: str, target: config.Target):
        with open(f'{config.RESULTS_DIR}/{target.name}_{self.key}.out.txt', 'w') as fh:
            fh.write(result)


all_commands = [
    CommandPing(COMMAND_KEYS.PING),
    CommandGenericScript(COMMAND_KEYS.LINENUM),
    CommandGenericScript(COMMAND_KEYS.LINPEAS)
]

for command_key in COMMAND_KEYS:
    for command in all_commands:
        if command.key == command_key.value:
            break
    else:
        raise Exception(f'Command for key {command_key.value} missing')
