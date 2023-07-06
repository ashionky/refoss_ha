from __future__ import annotations

from logging import Logger, getLogger

from typing import Final


DOMAIN: Final = "refoss"

LOGGER: Logger = getLogger(__package__)
DEVICE_LIST_COORDINATOR = "device_list_coordinator"
SOCKET_DISCOVER_UPDATE_INTERVAL = 30               #  Device Discovered Once on LAN every 30 seconds
DEFAULT_COMMAND_TIMEOUT = 10.0


HA_SWITCH = "switch"


MEROSS_PLATFORMS: Final = [
    HA_SWITCH,
]




