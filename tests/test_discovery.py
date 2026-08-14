"""Tests for Refoss discovery."""

import json
from unittest.mock import Mock

import pytest

from refoss_ha.discovery import Discovery


@pytest.mark.asyncio
async def test_broadcast_discovery() -> None:
    """Test discovery uses the broadcast address by default."""
    discovery = Discovery()
    discovery.transport = Mock()

    await discovery.broadcast_msg()

    data, address = discovery.transport.sendto.call_args.args
    assert json.loads(data) == {
        "id": "48cbd88f969eb3c486085cfe7b5eb1e4",
        "devName": "*",
    }
    assert address == ("255.255.255.255", 9988)


@pytest.mark.asyncio
async def test_unicast_discovery() -> None:
    """Test discovery can target a specific host."""
    discovery = Discovery()
    discovery.transport = Mock()

    await discovery.broadcast_msg(host="192.0.2.10")

    assert discovery.transport.sendto.call_args.args[1] == ("192.0.2.10", 9988)
