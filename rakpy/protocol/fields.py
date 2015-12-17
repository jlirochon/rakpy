# -*- coding: utf-8 -*-
from struct import pack, unpack


class Field(object):
    LENGTH = None

    def contribute_to_class(self, cls, name):
        cls._meta.add_field(self, name)

    @classmethod
    def guess_length(cls, data):
        return cls.LENGTH

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
    def decode(cls, data):
        return unpack(cls.PACK_FORMAT, data)[0]

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
    LENGTH_FIELD = UnsignedShortField

    @classmethod
    def guess_length(cls, data):
        # encoded data length + actual data
        return cls.LENGTH_FIELD.LENGTH + cls.LENGTH_FIELD.decode(data[:cls.LENGTH_FIELD.LENGTH])

    @classmethod
    def decode(cls, data):
        return data[cls.LENGTH_FIELD.LENGTH:].decode("utf-8")

    @classmethod
    def encode(cls, value):
        value = value.encode("utf-8")
        return cls.LENGTH_FIELD.encode(len(value)) + value
