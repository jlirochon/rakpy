# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from struct import pack, unpack
from collections import namedtuple

import six

from rakpy.io import convert_to_stream, EndOfStreamException

Address = namedtuple("Address", "ip port version")
Address.__new__.__defaults__ = (None, None, 4)

Range = namedtuple("Range", "min_index max_index")


class Field(object):
    LENGTH = None

    def __init__(self, **options):
        self._options = options

    def contribute_to_class(self, cls, name):
        cls._meta.add_field(self, name)

    @classmethod
    def decode(cls, data):
        raise NotImplementedError()

    @classmethod
    def encode(cls, value):
        raise NotImplementedError()


class NumericField(Field):
    LENGTH = None
    PACK_FORMAT = None

    @classmethod
    def get_min_value(cls):
        raise NotImplementedError()

    @classmethod
    def get_max_value(cls):
        raise NotImplementedError()

    @classmethod
    @convert_to_stream("data")
    def decode(cls, data):
        return unpack(cls.PACK_FORMAT, data.read(cls.LENGTH))[0]

    @classmethod
    def encode(cls, value):
        if value < cls.get_min_value() or value > cls.get_max_value():
            raise OverflowError()
        return pack(cls.PACK_FORMAT, value)


class SignedNumericField(NumericField):

    @classmethod
    def get_min_value(cls):
        return -pow(2, 8 * cls.LENGTH - 1) + 1

    @classmethod
    def get_max_value(cls):
        return pow(2, 8 * cls.LENGTH - 1) - 1


class UnsignedNumericField(NumericField):

    @classmethod
    def get_min_value(cls):
        return 0

    @classmethod
    def get_max_value(cls):
        return pow(2, 8 * cls.LENGTH) - 1


class ByteField(SignedNumericField):
    LENGTH = 1
    PACK_FORMAT = "!b"


class UnsignedByteField(UnsignedNumericField):
    LENGTH = 1
    PACK_FORMAT = "!B"


class TriadField(UnsignedNumericField):
    LENGTH = 3
    PACK_FORMAT = "!I"

    @classmethod
    @convert_to_stream("data")
    def decode(cls, data):
        return unpack(cls.PACK_FORMAT, b"\x00" + data.read(cls.LENGTH))[0]

    @classmethod
    def encode(cls, value):
        return super(TriadField, cls).encode(value)[1:]


class UnsignedShortField(UnsignedNumericField):
    LENGTH = 2
    PACK_FORMAT = "!H"


class IntField(SignedNumericField):
    LENGTH = 4
    PACK_FORMAT = "!i"


class LongLongField(SignedNumericField):
    LENGTH = 8
    PACK_FORMAT = "!q"


class UnsignedLongLongField(UnsignedNumericField):
    LENGTH = 8
    PACK_FORMAT = "!Q"


class FloatField(NumericField):
    LENGTH = 4
    PACK_FORMAT = "!f"

    @classmethod
    def get_min_value(cls):
        return float("-inf")  # OverflowError will be raised at runtime

    @classmethod
    def get_max_value(cls):
        return float("inf")   # OverflowError will be raised at runtime

    @classmethod
    def encode(cls, value):
        return super(FloatField, cls).encode(float(value))

    @classmethod
    def decode(cls, data):
        return float(super(FloatField, cls).decode(data))


class DoubleField(FloatField):
    LENGTH = 8
    PACK_FORMAT = "!d"


class BoolField(Field):
    LENGTH = 1

    @classmethod
    def decode(cls, data):
        return bool(ByteField.decode(data))

    @classmethod
    def encode(cls, value):
        return ByteField.encode(bool(value))


class StringField(Field):

    @convert_to_stream("data")
    def decode(self, data):
        try:
            length = UnsignedShortField.decode(data)
        except EndOfStreamException:
            if self._options.get("required", True):
                raise
            return None
        return data.read(length).decode("utf-8")

    @classmethod
    def encode(cls, value):
        value = value.encode("utf-8")
        return UnsignedShortField.encode(len(value)) + value


class OptionsField(Field):
    LENGTH = 1

    @classmethod
    @convert_to_stream("data")
    def decode(cls, data):
        bits = ord(data.read(1))
        return {
            "reliability": (bits & 0b11100000) >> 5,
            "has_split": bool(bits & 0b00010000)
        }

    @classmethod
    def encode(cls, options):
        data = 0b00000000
        if options.get("has_split", False):
            data |= 0b00010000
        reliability = options.get("reliability", 0x00) << 5
        data |= reliability
        return six.int2byte(data)


class AddressField(Field):
    LENGTH = (1 + 4) * UnsignedByteField.LENGTH + 2 * UnsignedShortField.LENGTH

    @classmethod
    @convert_to_stream("data")
    def decode(cls, data):
        # version
        version = UnsignedByteField.decode(data)
        # ip
        ip = []
        for part in range(4):
            ip.append(UnsignedByteField.decode(data))
        ip = ".".join(str(part) for part in ip)
        # port
        port = UnsignedShortField.decode(data)
        return Address(version=version, ip=ip, port=port)

    @classmethod
    def encode(cls, address):
        # version
        data = UnsignedByteField.encode(address.version)
        # ip
        for part in address.ip.split("."):
            data += UnsignedByteField.encode(int(part))
        # port
        data += UnsignedShortField.encode(address.port)
        return data


class RangeListField(Field):

    @classmethod
    @convert_to_stream("data")
    def decode(cls, data):
        range_list = []
        length = UnsignedShortField.decode(data)
        for i in range(length):
            min_equals_max = BoolField.decode(data)
            min_index = TriadField.decode(data)
            max_index = min_index if min_equals_max else max(TriadField.decode(data), min_index + 512)
            range_list.append(Range(min_index=min_index, max_index=max_index))
        return range_list

    @classmethod
    def encode(cls, range_list):
        data = UnsignedShortField.encode(len(range_list))
        for range_ in range_list:
            min_equals_max = range_.min_index == range_.max_index
            data += BoolField.encode(min_equals_max)
            data += TriadField.encode(range_.min_index)
            if not min_equals_max:
                data += TriadField.encode(range_.max_index)
        return data


class PaddingField(Field):

    @convert_to_stream("data")
    def decode(self, data):
        offset = self._options.get('offset', 0)
        return len(data.readall()) + offset

    def encode(self, value):
        offset = self._options.get('offset', 0)
        return max(0, value - offset) * b"\x00"
