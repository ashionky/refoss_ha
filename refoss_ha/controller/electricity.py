"""ElectricityXMix."""
import logging
import traceback

from ..enums import Namespace
from ..device import DeviceInfo
from .device import BaseDevice
from ..exceptions import DeviceTimeoutError

_LOGGER = logging.getLogger(__name__)


class ElectricityXMix(BaseDevice):
    """A device."""

    def __init__(self, device: DeviceInfo):
        """Initialize."""
        self.device = device
        self.status = {}
        super().__init__(device)

    def get_value(self, channel: int, subkey: str):
        """
        Returns the value for the given channel and subkey, or None if not found.
        """
        channel_status = self.status.get(channel)
        if channel_status is not None and subkey in channel_status:
            return channel_status[subkey]
        return None

    async def async_handle_update(self):
        """Update device state,65535 get all channel."""
        payload = {"electricity": {"channel": 65535}}
        res = await self.async_execute_cmd(
            device_uuid=self.uuid,
            method="GET",
            namespace=Namespace.CONTROL_ELECTRICITYX,
            payload=payload,
        )
        if res is not None:
            data = res.get("payload", {})
            await self.async_update_push_state(
                Namespace.CONTROL_ELECTRICITYX.value, data, self.uuid
            )

    async def async_update_push_state(self, namespace: str, data: dict, uuid: str):
        """Update push state."""

        if namespace == Namespace.CONTROL_ELECTRICITYX.value:
            payload = data["electricity"]
            if payload is None:
                _LOGGER.debug(
                    f"{data} could not find 'electricity' attribute in push notification data"
                )

            elif isinstance(payload, list):
                for state in payload:
                    channel = state["channel"]
                    self.status[channel] = state
