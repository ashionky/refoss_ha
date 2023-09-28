"""util."""
import logging
import re

LOGGER = logging.getLogger(__name__)

camel_pat = re.compile(r"([A-Z])")
under_pat = re.compile(r"_([a-z])")


def verify_msg(data: dict) -> str | None:
    """verify push msg."""
    header = data.get("header", {})
    namespace = header.get("namespace", None)
    uuid = header.get("uuid", None)
    payload = data.get("payload", None)
    if namespace is None or uuid is None or payload is None:
        return None
    return uuid


def _camel_to_underscore(key):
    return camel_pat.sub(lambda x: "_" + x.group(1).lower(), key)


def _underscore_to_camel(key):
    return under_pat.sub(lambda x: x.group(1).upper(), key)


class BaseDictPayload:
    """Base class for."""

    def __init__(self, *args, **kwargs) -> None:
        """init."""

    @classmethod
    def from_dict(cls, json_dict: dict):
        """from_dict."""
        new_dict = {
            _camel_to_underscore(key): value for (key, value) in json_dict.items()
        }
        obj = cls(**new_dict)
        return obj

    def to_dict(self) -> dict:
        """to_dict."""
        res = {}
        for k, v in vars(self).items():
            new_key = _underscore_to_camel(k)
            res[new_key] = v
        return res
