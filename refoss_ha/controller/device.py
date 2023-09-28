"""BaseDevice."""
from __future__ import annotations

import json
import asyncio
from typing import Union
from collections.abc import Awaitable, Callable

from ..enums import Namespace
from ..http_device import DeviceInfo


class BaseDevice:
    """ "BaseDevice."""

    def __init__(self, device_info: DeviceInfo):
        """Construct BaseDevice."""
        self.device_info = device_info
        self.uuid = device_info.uuid
        self.dev_name = device_info.dev_name
        self.device_type = device_info.device_type
        self.fmware_version = device_info.fmware_version
        self.hdware_version = device_info.hdware_version
        self.inner_ip = device_info.inner_ip
        self.port = device_info.port
        self.mac = device_info.mac
        self.sub_type = device_info.sub_type
        self.channels = json.loads(device_info.channels)
        self.online = True
        self._push_coros = []

    async def async_handle_push_notification(
            self, namespace: str, data: dict, uuid: str
    ) -> None:
        """Handle."""
        self.online = True
        for c in self._push_coros:
            await c(namespace=namespace, data=data, uuid=uuid)

    def register_push_notification_handler_coroutine(
            self, coro: Callable[[str, dict, str], Awaitable]
    ) -> None:
        """Register."""
        if not asyncio.iscoroutinefunction(coro):
            return
        if coro in self._push_coros:
            return
        self._push_coros.append(coro)

    def unregister_push_notification_handler_coroutine(
            self, coro: Callable[[str, dict, str], Awaitable]
    ) -> None:
        """unregister_push_notification_handler_coroutine."""
        if coro in self._push_coros:
            self._push_coros.remove(coro)

    async def async_update_push_state(
            self, namespace: str, data: dict, uuid: str
    ):
        """Handle push state."""

    async def async_handle_update(self, channel=0):
        """update device state."""

    async def async_execute_cmd(
            self,
            device_uuid: str,
            method: str,
            namespace: Union[Namespace, str],
            payload: dict,
            timeout: int = 5,
    ):
        """Execute command."""
        res = await self.device_info.async_execute_cmd(
            device_uuid=device_uuid,
            method=method,
            namespace=namespace,
            payload=payload,
            timeout=timeout,
        )
        if res is None:
            self.online = False
        else:
            self.online = True
        return res
