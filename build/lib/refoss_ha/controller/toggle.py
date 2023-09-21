"""ToggleXMix."""
import logging
import traceback

from ..enums import Namespace
from ..http_device import HttpDeviceInfo
from .device import BaseDevice

_LOGGER = logging.getLogger(__name__)


class ToggleXMix(BaseDevice):
    """A device."""

    def __init__(self, device: HttpDeviceInfo):
        """Initialize."""
        self.device = device
        self.status = {}
        super().__init__(device)

    def is_on(self, channel=0) -> bool | None:
        """is_on(self, channel)."""
        return self.status.get(channel, None)

    async def async_handle_update(self):
        """Update device state."""
        payload = {"togglex": {"channel": 0}}
        res = await self.async_execute_cmd(
            device_uuid=self.uuid,
            method="GET",
            namespace=Namespace.CONTROL_TOGGLEX,
            payload=payload,
        )
        if res is not None:
            data = res.get("payload", {})
            await self.async_update_push_state(Namespace.CONTROL_TOGGLEX.value, data, self.uuid)

    async def async_update_push_state(
            self, namespace: str, data: dict, uuid: str
    ):
        """Update push state."""
        try:
            if namespace == Namespace.CONTROL_TOGGLEX.value:
                payload = data["togglex"]
                if payload is None:
                    _LOGGER.debug(
                        f"{data} could not find 'togglex' attribute in push notification data"
                    )

                elif isinstance(payload, list):
                    for c in payload:
                        channel = c["channel"]
                        switch_state = c["onoff"] == 1
                        self.status[channel] = switch_state

                elif isinstance(payload, dict):
                    channel = payload["channel"]
                    switch_state = payload["onoff"] == 1
                    self.status[channel] = switch_state

        except Exception as e:
            print("error", traceback.format_exc())

    async def async_turn_off(self, channel=0) -> None:
        """Turn off."""
        payload = {"togglex": {"onoff": 0, "channel": channel}}
        res = await self.async_execute_cmd(
            device_uuid=self.uuid,
            method="SET",
            namespace=Namespace.CONTROL_TOGGLEX,
            payload=payload,
        )
        if res is not None:
            self.status[channel] = False

    async def async_turn_on(self, channel=0) -> None:
        """Turn on."""
        payload = {"togglex": {"onoff": 1, "channel": channel}}
        res = await self.async_execute_cmd(
            device_uuid=self.uuid,
            method="SET",
            namespace=Namespace.CONTROL_TOGGLEX,
            payload=payload,
        )
        if res is not None:
            self.status[channel] = True

    async def async_toggle(self, channel=0) -> None:
        """Toggle."""
        if self.is_on(channel=channel):
            await self.async_turn_off(channel=channel)
        else:
            await self.async_turn_on(channel=channel)
