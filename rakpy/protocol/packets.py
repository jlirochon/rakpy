# -*- coding: utf-8 -*-
#
# WARNING: auto-generated by generate.py, do not edit this code !
#
from rakpy.protocol import registry
from rakpy.protocol import fields
from rakpy.protocol import Packet


@registry.add
class Acknowledge(Packet):
    packet_ranges = fields.RangeListField()

    class Meta(object):
        id = 0xc0
        structure = ("packet_ranges",)


@registry.add
class Unacknowledge(Packet):
    packet_ranges = fields.RangeListField()

    class Meta(object):
        id = 0xa0
        structure = ("packet_ranges",)


@registry.add
class AdvertiseSystem(Packet):
    ping_id = fields.LongLongField()
    server_guid = fields.LongLongField()
    server_name = fields.StringField()

    class Meta(object):
        id = 0x1d
        structure = ("ping_id", "server_guid", "__magic__", "server_name")


@registry.add
class ConnectionRequest(Packet):
    client_guid = fields.LongLongField()
    send_ping = fields.LongLongField()
    use_security = fields.BoolField()

    class Meta(object):
        id = 0x09
        structure = ("client_guid", "send_ping", "use_security")


@registry.add
class OpenConnectionReply1(Packet):
    server_guid = fields.LongLongField()
    use_security = fields.BoolField()
    mtu_size = fields.UnsignedShortField()

    class Meta(object):
        id = 0x06
        structure = ("__magic__", "server_guid", "use_security", "mtu_size")


@registry.add
class OpenConnectionReply2(Packet):
    server_guid = fields.LongLongField()
    address = fields.AddressField()
    mtu_size = fields.UnsignedShortField()
    use_security = fields.BoolField()

    class Meta(object):
        id = 0x08
        structure = ("__magic__", "server_guid", "address", "mtu_size", "use_security")


@registry.add
class OpenConnectionRequest1(Packet):
    protocol = fields.ByteField()
    mtu_size = fields.PaddingField(offset=18)

    class Meta(object):
        id = 0x05
        structure = ("__magic__", "protocol", "mtu_size")


@registry.add
class OpenConnectionRequest2(Packet):
    server_address = fields.AddressField()
    mtu_size = fields.UnsignedShortField()
    client_guid = fields.LongLongField()

    class Meta(object):
        id = 0x07
        structure = ("__magic__", "server_address", "mtu_size", "client_guid")


@registry.add
class ConnectedPing(Packet):
    ping_id = fields.LongLongField()

    class Meta(object):
        id = 0x00
        structure = ("ping_id",)


@registry.add
class ConnectedPong(Packet):
    ping_id = fields.LongLongField()

    class Meta(object):
        id = 0x03
        structure = ("ping_id",)


@registry.add
class UnconnectedPing(Packet):
    ping_id = fields.LongLongField()
    client_guid = fields.LongLongField()

    class Meta(object):
        id = 0x01
        structure = ("ping_id", "__magic__", "client_guid")


@registry.add
class UnconnectedPingOpenConnections(Packet):
    ping_id = fields.LongLongField()
    client_guid = fields.LongLongField()

    class Meta(object):
        id = 0x02
        structure = ("ping_id", "__magic__", "client_guid")


@registry.add
class UnconnectedPong(Packet):
    ping_id = fields.LongLongField()
    server_guid = fields.LongLongField()
    server_name = fields.StringField()

    class Meta(object):
        id = 0x1c
        structure = ("ping_id", "server_guid", "__magic__", "server_name")
