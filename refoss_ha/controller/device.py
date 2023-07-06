from __future__ import annotations

import asyncio
import json
import logging
from typing import  Callable, Awaitable


from ..enums import Namespace
from ..http_device import HttpDeviceInfo



_LOGGER = logging.getLogger(__name__)


class BaseDevice(object):
    def __init__(self, base_device:HttpDeviceInfo):
        self.uuid = base_device.uuid
        self.dev_name = base_device.dev_name
        self.device_type = base_device.device_type
        self.fmware_version = base_device.fmware_version
        self.hdware_version = base_device.hdware_version
        self.inner_ip = base_device.inner_ip
        self.port = base_device.port
        self.mac = base_device.mac
        self.sub_type = base_device.sub_type
        self._push_coros = []
        self.channels =json.loads(base_device.channels)





    async def async_handle_push_notification(self, namespace: Namespace,data:dict,uuid:str) -> bool:

        for c in self._push_coros:
            try:
                await c(namespace=namespace, data=data, uuid=uuid)
            except Exception as e:
                print("Error processing")
        return False

    async def async_handle_update(self, namespace: Namespace, data: dict) -> bool:
        pass

    async def async_update_push_state(self, namespace: Namespace, data: dict,uuid:str) -> bool:
        pass


    async def async_update(self) -> None:
        pass

    def register_push_notification_handler_coroutine(self, coro: Callable[[Namespace, dict, str], Awaitable]) -> None:

        if not asyncio.iscoroutinefunction(coro):
            raise ValueError("The coro parameter must be a coroutine")
        if coro in self._push_coros:
            _LOGGER.error(f"Coroutine {coro} was already added to event handlers of this device")
            return
        self._push_coros.append(coro)

    def unregister_push_notification_handler_coroutine(self, coro: Callable[[str, dict, str], Awaitable]) -> None:

        if coro in self._push_coros:
            self._push_coros.remove(coro)
        else:
            _LOGGER.error(f"Coroutine {coro} was not registered as handler for this device")

