from __future__ import annotations

from logging import Logger, getLogger

from typing import Final


DOMAIN: Final = "refoss"

LOGGER: Logger = getLogger(__package__)
DEVICE_LIST_COORDINATOR = "device_list_coordinator"
SOCKET_DISCOVER_UPDATE_INTERVAL = 30  #  Device Discovered Once on LAN every 30 seconds
DEFAULT_COMMAND_TIMEOUT = 10.0
PUSH = "PUSH"


HA_SWITCH = "switch"


PLATFORMS: Final = [
    HA_SWITCH,
]
