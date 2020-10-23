import socket
from . import config
import threading
from . import communication


def get_next_free_port() -> int:
    config.last_used_port_lock.acquire()
    try:
        while True:
            config.last_used_port += 1
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if sock.connect_ex(('localhost', config.last_used_port)) == 0:
                    break  # open port found

    finally:
        config.last_used_port_lock.release()
        return config.last_used_port


def new_target(remote_ip: str) -> int:
    new_port = get_next_free_port()
    target = config.Target(remote_ip, new_port, remote_ip)
    config.targets.append(target)

    def initialise_connection_and_wait():
        target.sock.accept()
        target.set_status(config.TargetStatus.CONNECTED)
        communication.wait_for_commands_from_target(target)

    threading.Thread(target=initialise_connection_and_wait)
    return new_port

