import libtmux

import subprocess


class Tmux:
    server = libtmux.Server()
    session: libtmux.Session

    @staticmethod
    def connect():
        if len(Tmux.server.list_sessions()) != 1:
            raise Exception('Please only have one tmux session running')

    @staticmethod
    def new_window_with_cmd(cmd: str, window_name=None):
        subprocess.Popen(f'tmux new-window {f"-n {window_name}" if window_name is not None else ""} {cmd}')
