from . import config
import threading
from . import communication


def new_target(remote_ip: str) -> int:
    target = config.Target(remote_ip, remote_ip)
    config.targets.append(target)

    def initialise_connection_and_wait():
        target.sock = target.sock.accept()[0]
        target.set_status(config.TargetStatus.CONNECTED)
        communication.wait_for_results_from_target(target)

    threading.Thread(target=initialise_connection_and_wait, daemon=True).start()
    return target.local_port


