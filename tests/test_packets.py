# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
import six

from rakpy.protocol import decode_packet
from rakpy.protocol.exceptions import UnknownPacketException, RemainingDataException
from rakpy.protocol import packets


def test_packet_id():

    class DummyPacket(packets.Packet):
        class Meta(object):
            id = 0x42
            structure = ()

    packet = DummyPacket()

    # setter
    with pytest.raises(AttributeError):
        packet.id = 0xff

    # getter
    assert packet.id == 0x42


def test_decode_unconnected_ping():

    # invalid packet id
    with pytest.raises(ValueError):
        packets.UnconnectedPing(b"\x42\x00\x00\x00\x00")

    data = (
        b"\x01\x00\x00\x00\x00\x00\x02\xf3\x47\x00\xff\xff\x00\xfe\xfe\xfe\xfe"
        b"\xfd\xfd\xfd\xfd\x12\x34\x56\x78\x00\x05\x27\x00\xaa\x0a\x23\xa3"
    )
    packet = packets.UnconnectedPing(data)
    assert packet.time == 193351
    assert packet.client_guid == 1450258689827747
    assert six.text_type(packet) == "UnconnectedPing(time=193351, client_guid=1450258689827747)"


def test_decode_packet():
    data = (
        b"\x01\x00\x00\x00\x00\x00\x02\xf3\x47\x00\xff\xff\x00\xfe\xfe\xfe\xfe"
        b"\xfd\xfd\xfd\xfd\x12\x34\x56\x78\x00\x05\x27\x00\xaa\x0a\x23\xa3"
    )
    packet = decode_packet(data)
    assert packet.id == 0x01
    assert type(packet) == packets.UnconnectedPing


def test_decode_invalid_packet():
    with pytest.raises(UnknownPacketException):
        decode_packet(b"\xff\x00\x00\x00\x00")


def test_decode_packed_with_remaining_data():
    data = (
        b"\x01\x00\x00\x00\x00\x00\x02\xf3\x47\x00\xff\xff\x00\xfe\xfe\xfe\xfe"
        b"\xfd\xfd\xfd\xfd\x12\x34\x56\x78\x00\x05\x27\x00\xaa\x0a\x23\xa3"
    ) + b"LOL"
    with pytest.raises(RemainingDataException):
        decode_packet(data)


def test_decode_disconnection_notification():
    packet = decode_packet(b"\x15")
    assert packet.id == 0x15
    assert type(packet) == packets.DisconnectionNotification
