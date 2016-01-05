# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from rakpy.io import EndOfStreamException
from rakpy.protocol import fields, MagicField
from rakpy.protocol.const import MAGIC
from rakpy.protocol.fields import Address, Range


def test_not_implemented_methods():

    class TestField(fields.Field):
        pass

    field = TestField()
    with pytest.raises(NotImplementedError):
        field.decode(None)
    with pytest.raises(NotImplementedError):
        field.encode(None)

    class TestNumericField(fields.NumericField):
        pass

    field = TestNumericField()
    with pytest.raises(NotImplementedError):
        field.get_min_value()
    with pytest.raises(NotImplementedError):
        field.get_max_value()


def test_magic_field():

    field = MagicField()

    # decode valid data
    assert field.decode(MAGIC) == b""

    # decode invalid data
    with pytest.raises(ValueError):
        field.decode(16 * b"\x42")

    # encode
    assert field.encode(b"") == MAGIC
    assert field.encode(b"\x42") == MAGIC
    assert field.encode(b"whatever") == MAGIC


def test_byte_field():
    field = fields.ByteField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-128)

    # min value
    assert field.encode(-127) == b"\x81"
    assert field.decode(b"\x81") == -127

    # 0
    assert field.encode(0) == b"\x00"
    assert field.decode(b"\x00") == 0

    # max value
    assert field.encode(127) == b"\x7f"
    assert field.decode(b"\x7f") == 127

    # to high
    with pytest.raises(OverflowError):
        field.encode(128)


def test_triad_field():
    field = fields.TriadField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-1)

    # 0
    assert field.encode(0) == b"\x00\x00\x00"
    assert field.decode(b"\x00\x00\x00") == 0

    # 1
    assert field.encode(1) == b"\x00\x00\x01"
    assert field.decode(b"\x00\x00\x01") == 1

    # 256
    assert field.encode(256) == b"\x00\x01\x00"
    assert field.decode(b"\x00\x01\x00") == 256

    # max value
    assert field.encode(16777215) == b"\xff\xff\xff"
    assert field.decode(b"\xff\xff\xff") == 16777215

    # to high
    with pytest.raises(OverflowError):
        field.encode(16777216)


def test_unsigned_byte_field():
    field = fields.UnsignedByteField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-1)

    # 0 (min value)
    assert field.encode(0) == b"\x00"
    assert field.decode(b"\x00") == 0

    # max value
    assert field.encode(255) == b"\xff"
    assert field.decode(b"\xff") == 255

    # to high
    with pytest.raises(OverflowError):
        field.encode(256)


def test_bool_field():
    field = fields.BoolField()

    # False
    assert field.encode(False) == b"\x00"
    assert field.encode(None) == b"\x00"
    assert field.encode(0) == b"\x00"
    assert field.encode("") == b"\x00"
    assert field.decode(b"\x00") == False

    # True
    assert field.encode(True) == b"\x01"
    assert field.decode(b"\x01") == True

    # Anything is true
    assert field.encode(1) == b"\x01"
    assert field.encode("hey") == b"\x01"


def test_unsigned_short_field():
    field = fields.UnsignedShortField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-1)

    # 0 (min value)
    assert field.encode(0) == b"\x00\x00"
    assert field.decode(b"\x00\x00") == 0

    # max value
    assert field.encode(65535) == b"\xff\xff"
    assert field.decode(b"\xff\xff") == 65535

    # to high
    with pytest.raises(OverflowError):
        field.encode(65536)


def test_int_field():
    field = fields.IntField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-2147483648)

    # min value
    assert field.encode(-2147483647) == b"\x80\x00\x00\x01"
    assert field.decode(b"\x80\x00\x00\x01") == -2147483647

    # 0
    assert field.encode(0) == b"\x00\x00\x00\x00"
    assert field.decode(b"\x00\x00\x00\x00") == 0

    # max value
    assert field.encode(2147483647) == b"\x7f\xff\xff\xff"
    assert field.decode(b"\x7f\xff\xff\xff") == 2147483647

    # to high
    with pytest.raises(OverflowError):
        field.encode(2147483648)


def test_long_long_field():
    field = fields.LongLongField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-9223372036854775808)

    # min value
    assert field.encode(-9223372036854775807) == b"\x80\x00\x00\x00\x00\x00\x00\x01"
    assert field.decode(b"\x80\x00\x00\x00\x00\x00\x00\x01") == -9223372036854775807

    # 0
    assert field.encode(0) == b"\x00\x00\x00\x00\x00\x00\x00\x00"
    assert field.decode(b"\x00\x00\x00\x00\x00\x00\x00\x00") == 0

    # max value
    assert field.encode(9223372036854775807) == b"\x7f\xff\xff\xff\xff\xff\xff\xff"
    assert field.decode(b"\x7f\xff\xff\xff\xff\xff\xff\xff") == 9223372036854775807

    # too high
    with pytest.raises(OverflowError):
        field.encode(9223372036854775808)


def test_string_field():
    field = fields.StringField()

    # str
    assert field.encode("Hello !") == b"\x00\x07Hello !"
    assert field.decode(b"\x00\x07Hello !") == "Hello !"

    # very long str
    long_str = (
        "wojfewjfwpejfjewofjwjfowefojwjfoewjofijewofjewojfeowjfowjfowejoifjewojfweoioifjowjowfjwjiwojoifjowfe"
        "fwjfweofhoiehwefoiegfurewgkwjenvoerbvoubreuwbverubwvuirbewuvibeiruwbvuierwbviuerbvubeuvibuebwviuruwe"
        "wojfewjfwpejfjewofjwjfowefojwjfoewjofijewofjewojfeowjfowjfowejoifjewojfweoioifjowjowfjwjiwojoifjowfe"
        "fwjfweofhoiehwefoiegfurewgkwjenvoerbvoubreuwbverubwvuirbewuvibeiruwbvuierwbviuerbvubeuvibuebwviuruwe"
    )
    encoded = field.encode(long_str)
    assert encoded[:2] == b"\x01\x90"
    assert encoded[2:] == long_str.encode("utf-8")
    assert field.decode(b"\x01\x90" + long_str.encode("utf-8")) == long_str

    # unicode
    assert field.encode("ボールト") == b"\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    assert field.decode(b"\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88") == "ボールト"

    # raise if data is empty
    with pytest.raises(EndOfStreamException):
        field.decode(b"")

    # do not raise if required=False
    field = fields.StringField(required=False)
    assert field.decode(b"") is None


def test_float_field():
    field = fields.FloatField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-4 * pow(10, 38))

    # some very low value
    low_value = -3.2345678 * pow(10, 38)
    assert field.encode(low_value) == b"\xff\x73\x57\x83"
    assert abs(field.decode(b"\xff\x73\x57\x83") - low_value) < abs(low_value * pow(10, -7))

    # still some negative value
    assert field.encode(-300) == b"\xc3\x96\x00\x00"
    assert field.decode(b"\xc3\x96\x00\x00") == -300

    # 0
    assert field.encode(0) == b"\x00\x00\x00\x00"
    assert field.decode(b"\x00\x00\x00\x00") == 0

    # some positive value
    assert field.encode(300) == b"\x43\x96\x00\x00"
    assert field.decode(b"\x43\x96\x00\x00") == 300

    # some very high value
    high_value = 3.2345678 * pow(10, 38)
    assert field.encode(high_value) == b"\x7f\x73\x57\x83"
    assert abs(field.decode(b"\x7f\x73\x57\x83") - high_value) < abs(high_value * pow(10, -7))


def test_double_field():
    field = fields.DoubleField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-4 * pow(10, 400))

    # some very low value
    low_value = -3.2345678 * pow(10, 64)
    assert field.encode(low_value) == b"\xcd\x53\xa8\x30\xf3\x15\x89\x61"
    assert abs(field.decode(b"\xcd\x53\xa8\x30\xf3\x15\x89\x61") - low_value) < abs(low_value * pow(10, -8))

    # still some negative value
    assert field.encode(-300) == b"\xc0\x72\xc0\x00\x00\x00\x00\x00"
    assert field.decode(b"\xc0\x72\xc0\x00\x00\x00\x00\x00") == -300

    # 0
    assert field.encode(0) == b"\x00\x00\x00\x00\x00\x00\x00\x00"
    assert field.decode(b"\x00\x00\x00\x00\x00\x00\x00\x00") == 0

    # some positive value
    assert field.encode(300) == b"\x40\x72\xc0\x00\x00\x00\x00\x00"
    assert field.decode(b"\x40\x72\xc0\x00\x00\x00\x00\x00") == 300

    # some very high value
    high_value = 3.2345678 * pow(10, 64)
    assert field.encode(high_value) == b"\x4d\x53\xa8\x30\xf3\x15\x89\x61"
    assert abs(field.decode(b"\x4d\x53\xa8\x30\xf3\x15\x89\x61") - high_value) < abs(high_value * pow(10, -8))


options_field_data = [
    # split
    (dict(has_split=False, reliability=0x00), b"\x00"),  # 0b00000000
    (dict(has_split=True, reliability=0x00), b"\x10"),  # 0b00010000
    # reliability
    (dict(has_split=False, reliability=0x01), b"\x20"),  # 0b00100000
    (dict(has_split=False, reliability=0x02), b"\x40"),  # 0b01000000
    (dict(has_split=False, reliability=0x03), b"\x60"),  # 0b01100000
    (dict(has_split=False, reliability=0x04), b"\x80"),  # 0b10000000
    (dict(has_split=False, reliability=0x05), b"\xa0"),  # 0b10100000
    (dict(has_split=False, reliability=0x06), b"\xc0"),  # 0b11000000
    (dict(has_split=False, reliability=0x07), b"\xe0"),  # 0b11100000
]


@pytest.mark.parametrize("decoded,encoded", options_field_data)
def test_options_field(encoded, decoded):
    field = fields.OptionsField()
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded


address_field_data = [
    (Address(ip="127.0.0.1", port=19132, version=4), b"\x04\x7f\x00\x00\x01\x4a\xbc"),
    (Address(ip="192.168.0.42", port=29132, version=4), b"\x04\xc0\xa8\x00\x2a\x71\xcc")
]


@pytest.mark.parametrize("decoded,encoded", address_field_data)
def test_address_field(encoded, decoded):
    field = fields.AddressField()
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded


range_list_field_data = [
    ([Range(min_index=0, max_index=0)], b"\x00\x01\x01\x00\x00\x00"),
    ([Range(min_index=65536, max_index=327680)], b"\x00\x01\x00\x01\x00\x00\x05\x00\x00"),
    ([Range(min_index=851968, max_index=917504)], b"\x00\x01\x00\x0d\x00\x00\x0e\x00\x00"),
    ([Range(min_index=5373952, max_index=5373952), Range(min_index=7471104, max_index=7536640)],
        b"\x00\x02\x01\x52\x00\x00\x00\x72\x00\x00\x73\x00\x00"),
    ([Range(min_index=9568256, max_index=9568256)], b"\x00\x01\x01\x92\x00\x00"),
]


@pytest.mark.parametrize("decoded,encoded", range_list_field_data)
def test_range_list_field(encoded, decoded):
    field = fields.RangeListField()
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded


padding_field_data = [
    (0, 0, b""),
    (0, 1, b"\x00"),
    (0, 5, b"\x00\x00\x00\x00\x00"),
    (0, 20, b"\x00" * 20),
    (0, 1500, b"\x00" * 1500),
    (18, 18, b""),
    (18, 19, b"\x00"),
    (18, 23, b"\x00\x00\x00\x00\x00"),
    (18, 20, b"\x00" * 2),
    (18, 1500, b"\x00" * 1482),
]


@pytest.mark.parametrize("offset,decoded,encoded", padding_field_data)
def test_padding_field(offset, encoded, decoded):
    field = fields.PaddingField(offset=offset)
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded
