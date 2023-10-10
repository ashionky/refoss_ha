"""socket_server."""
import asyncio
from asyncio import Task
import json
import logging
import socket
from typing import cast, List, Coroutine
from .device import DeviceInfo

_LOGGER = logging.getLogger(__name__)


class Listener:
    """Base class for device discovery events."""

    async def device_found(self, device_info: DeviceInfo) -> None:
        """Called any time a new (unique) device is found on the network."""

    async def device_update(self, device_info: DeviceInfo) -> None:
        """Called any time an up address for a device has changed on the network."""


def socket_init() -> socket.socket:
    """socket_init."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 9989))
    return sock


class Discovery(asyncio.DatagramProtocol, Listener):
    """Socket server."""

    def __init__(self) -> None:
        self._device_infos = {}
        self._listeners = []
        self._tasks = []
        self._loop = asyncio.get_event_loop()

    @property
    def tasks(self) -> List[Coroutine]:
        """Returns the outstanding tasks waiting completion."""
        return self._tasks

    @property
    def devices(self) -> List[DeviceInfo]:
        """Return the current known list of devices."""
        values_list = list(map(lambda x: x[1], self._device_infos.items()))
        return values_list

    def _task_done_callback(self, task):
        if task.exception():
            _LOGGER.exception("Uncaught exception", exc_info=task.exception())
        self._tasks.remove(task)

    def _create_task(self, coro) -> Task:
        """Create and track tasks that are being created for events."""
        task = self._loop.create_task(coro)
        self._tasks.append(task)
        task.add_done_callback(self._task_done_callback)
        return task

    def add_listener(self, listener: Listener):
        if not listener in self._listeners:
            self._listeners.append(listener)
            return [self._create_task(listener.device_found(x)) for x in self.devices]

    def remove_listener(self, listener: Listener) -> bool:
        if listener in self._listeners:
            self._listeners.remove(listener)
            return True
        return False

    def connection_made(self, transport: asyncio.transports.DatagramTransport) -> None:
        """Handle connection made."""
        self.transport = transport

    async def initialize(self) -> None:
        """Initialize socket server."""
        self.sock = socket_init()

        await self._loop.create_datagram_endpoint(lambda: self, sock=self.sock)

    async def broadcast_msg(self, wait_for: int = 0) -> List[DeviceInfo]:
        """Broadcast."""
        address = ("255.255.255.255", 9988)
        msg = json.dumps(
            {"id": "48cbd88f969eb3c486085cfe7b5eb1e4", "devName": "*"}
        ).encode("utf-8")
        try:
            self.transport.sendto(msg, address)
            if wait_for:
                await asyncio.sleep(wait_for)
                await asyncio.gather(*self.tasks, return_exceptions=True)
        except Exception as err:
            _LOGGER.debug(
                "broadcast_msg err: %s",
                err,
            )
        return self.devices

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle incoming datagram messages."""
        json_str = format(data.decode("utf-8"))
        data_dict = json.loads(json_str)
        if 'channels' in data_dict and 'uuid' in data_dict:
            device: DeviceInfo = DeviceInfo.from_dict(data_dict)
            if device is None:
                return
            self._loop.create_task(self.device_found(device))

    async def device_found(self, device_info: DeviceInfo) -> None:
        """Device is found."""
        uuid = device_info.uuid
        last_info: DeviceInfo = self._device_infos.get(uuid)

        if last_info is not None:
            if device_info.inner_ip != last_info.inner_ip:
                # ip address info may have been updated, so store the new info
                # and trigger a `device_update` event.
                self._device_infos[uuid] = device_info
                tasks = [l.device_update(device_info) for l in self._listeners]
                await asyncio.gather(*tasks, return_exceptions=True)
            return

        self._device_infos[uuid] = device_info

        tasks = [l.device_found(device_info) for l in self._listeners]
        await asyncio.gather(*tasks, return_exceptions=True)

    def clean_up(self) -> None:
        """Close."""
        self._device_infos = {}
        self._listeners = []
        self._tasks = []
