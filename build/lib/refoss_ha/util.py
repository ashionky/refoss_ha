import logging
import re
import psutil
import os
import uuid
from typing import List


_LOGGER = logging.getLogger(__name__)


camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def _camel_to_underscore(key):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), key)


def _underscore_to_camel(key):
    return under_pat.sub(lambda x: x.group(1).upper(), key)


class BaseDictPayload(object):
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def from_dict(cls, json_dict: dict):
        new_dict = {_camel_to_underscore(key): value for (key, value) in json_dict.items()}
        obj = cls(**new_dict)
        return obj

    def to_dict(self) -> dict:
        res = {}
        for k, v in vars(self).items():
            new_key = _underscore_to_camel(k)
            res[new_key] = v
        return res


def calculate_id(platform: str, uuid: str, channel: int, supplementary_classifiers: List[str] = None) -> str:
    base = "%s:%s:%d" % (platform, uuid, channel)
    if supplementary_classifiers is not None:
        extrastr = ":".join(supplementary_classifiers)
        if extrastr != "":
            extrastr = ":" + extrastr
        return base + extrastr
    return base


def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

def killSocketPid(port):
    # Obtain the process pid for the specified port
    pid = None
    for proc in psutil.process_iter():
        try:
            net_connections = proc.connections(kind='inet')
            for conn in net_connections:
                if conn.laddr[1] == port:
                    pid = proc.pid
                    break
            if pid is not None:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if pid is not None:
        try:
            os.kill(pid, 9)
            _LOGGER.info(f"Process with PID {pid} killed.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
