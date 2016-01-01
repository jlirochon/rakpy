# -*- coding: utf-8 -*-
from struct import pack, unpack
from collections import namedtuple

from rakpy.io import convert_to_stream

Address = namedtuple("Address", "ip port version")
Address.__new__.__defaults__ = (None, None, 4)


class Field(object):
    LENGTH = None

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

    @classmethod
    def get_min_value(cls):
        return 0

    @classmethod
    def get_max_value(cls):
        return pow(2, 8 * cls.LENGTH) - 1


class TriadField(UnsignedNumericField):
    LENGTH = 3
    PACK_FORMAT = "!I"

    @classmethod
    @convert_to_stream("data")
    def decode(cls, data):
        return unpack(cls.PACK_FORMAT, "\x00" + data.read(cls.LENGTH))[0]

    @classmethod
    def encode(cls, value):
        return super(TriadField, cls).encode(value)[1:]


class UnsignedShortField(UnsignedByteField):
    LENGTH = 2
    PACK_FORMAT = "!H"


class IntField(SignedNumericField):
    LENGTH = 4
    PACK_FORMAT = "!i"


class LongLongField(SignedNumericField):
    LENGTH = 8
    PACK_FORMAT = "!q"


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
    @classmethod
    @convert_to_stream("data")
    def decode(cls, data):
        length = UnsignedShortField.decode(data)
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
        return chr(data)


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
