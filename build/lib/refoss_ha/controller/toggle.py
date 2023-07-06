import logging
from typing import Optional

from ..http_device import HttpDeviceInfo
from .device import BaseDevice
from ..enums import Namespace


_LOGGER = logging.getLogger(__name__)


class ToggleXMix(BaseDevice):
    def __init__(self, device: HttpDeviceInfo):
        self.device = device
        self._channel_togglex_status = {}
        super().__init__(device)


    def is_on(self, channel=0) -> Optional[bool]:

        return self._channel_togglex_status.get(channel, None)

    async def async_handle_update(self, namespace: Namespace, data: dict) -> bool:

        updated = False
        if namespace == Namespace.SYSTEM_ALL:
            payload = data.get("payload",{}).get('all', {}).get('digest', {}).get('togglex', [])
            for c in payload:
                channel = c['channel']
                switch_state = c['onoff'] == 1
                self._channel_togglex_status[channel] = switch_state
            updated = True
        await super().async_handle_update(namespace=namespace, data=data)
        return  updated

    async def async_update_push_state(self, namespace: Namespace, data: dict,uuid:str) -> bool:

        updated = False
        if namespace == Namespace.CONTROL_TOGGLEX:

            payload = data.get('togglex')
            if payload is None:
                _LOGGER.warning(f"{self.__class__.__name__} could not find 'togglex' attribute in push notification data: {data}")

            elif isinstance(payload, list):
                for c in payload:
                    channel = c['channel']
                    switch_state = c['onoff'] == 1
                    self._channel_togglex_status[channel] = switch_state
                    updated = True

            elif isinstance(payload, dict):
                channel = payload['channel']
                switch_state = payload['onoff'] == 1
                self._channel_togglex_status[channel] = switch_state
                updated = True
        await super().async_update_push_state(namespace=namespace, data=data,uuid=uuid)
        return updated


    async def async_turn_off(self, channel=0) -> None:

        payload={'togglex': {"onoff": 0, "channel": channel}}
        await self.device.async_execute_cmd(device_uuid=self.uuid,method="SET",namespace=Namespace.CONTROL_TOGGLEX,payload=payload)

        self._channel_togglex_status[channel] = False

    async def async_turn_on(self, channel=0) -> None:

        payload={'togglex': {"onoff": 1, "channel": channel}}
        await self.device.async_execute_cmd(device_uuid=self.uuid,method="SET",namespace=Namespace.CONTROL_TOGGLEX,payload=payload)

        self._channel_togglex_status[channel] = True

    async def async_toggle(self, channel=0) -> None:
        if self.is_on(channel=channel):
            await self.async_turn_off(channel=channel)
        else:
            await self.async_turn_on(channel=channel)




