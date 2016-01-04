# -*- coding: utf-8 -*-
import pytest

from rakpy.protocol import PacketRegistry


def test_add():
    registry = PacketRegistry()

    class TestPacket(object):
        class _meta(object):
            id = 0x01

    # add TestPacket to registry
    assert 0x01 not in registry
    registry.add(TestPacket)
    assert 0x01 in registry
    assert registry[0x01] == TestPacket

    # TestPacket can't be added twice
    with pytest.raises(ValueError):
        registry.add(TestPacket)
