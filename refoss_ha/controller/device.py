"""BaseDevice."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import json
from typing import Union

from ..enums import Namespace
from ..http_device import HttpDeviceInfo


class BaseDevice:
    """ "BaseDevice."""

    def __init__(self, base_device: HttpDeviceInfo):
        """Construct BaseDevice."""
        self.http_device = base_device
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
        self.channels = json.loads(base_device.channels)
        self.online = True

    async def async_handle_push_notification(
            self, namespace: str, data: dict, uuid: str
    ) -> bool:
        """Handle."""
        self.online = True
        for c in self._push_coros:
            try:
                await c(namespace=namespace, data=data, uuid=uuid)
            except Exception:
                return False
        return False

    async def async_handle_update(self):
        """update device state."""

    async def async_update_push_state(
            self, namespace: str, data: dict, uuid: str
    ):
        """Handle push state."""

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

    async def async_execute_cmd(
            self,
            device_uuid: str,
            method: str,
            namespace: Union[Namespace, str],
            payload: dict,
            timeout: int = 5,
    ):
        """Execute command."""
        res = await self.http_device.async_execute_cmd(
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
