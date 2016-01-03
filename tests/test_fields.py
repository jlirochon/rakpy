# -*- coding: utf-8 -*-
import pytest

from rakpy.protocol import fields
from rakpy.protocol.fields import Address, Range


def test_byte_field():
    field = fields.ByteField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-128)

    # min value
    assert field.encode(-127) == "\x81"
    assert field.decode("\x81") == -127

    # 0
    assert field.encode(0) == "\x00"
    assert field.decode("\x00") == 0

    # max value
    assert field.encode(127) == "\x7f"
    assert field.decode("\x7f") == 127

    # to high
    with pytest.raises(OverflowError):
        field.encode(128)


def test_triad_field():
    field = fields.TriadField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-1)

    # 0
    assert field.encode(0) == "\x00\x00\x00"
    assert field.decode("\x00\x00\x00") == 0

    # 1
    assert field.encode(1) == "\x00\x00\x01"
    assert field.decode("\x00\x00\x01") == 1

    # 256
    assert field.encode(256) == "\x00\x01\x00"
    assert field.decode("\x00\x01\x00") == 256

    # max value
    assert field.encode(16777215) == "\xff\xff\xff"
    assert field.decode("\xff\xff\xff") == 16777215

    # to high
    with pytest.raises(OverflowError):
        field.encode(16777216)


def test_unsigned_byte_field():
    field = fields.UnsignedByteField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-1)

    # 0 (min value)
    assert field.encode(0) == "\x00"
    assert field.decode("\x00") == 0

    # max value
    assert field.encode(255) == "\xff"
    assert field.decode("\xff") == 255

    # to high
    with pytest.raises(OverflowError):
        field.encode(256)


def test_bool_field():
    field = fields.BoolField()

    # False
    assert field.encode(False) == "\x00"
    assert field.encode(None) == "\x00"
    assert field.encode(0) == "\x00"
    assert field.encode("") == "\x00"
    assert field.decode("\x00") == False

    # True
    assert field.encode(True) == "\x01"
    assert field.decode("\x01") == True

    # Anything is true
    assert field.encode(1) == "\x01"
    assert field.encode("hey") == "\x01"


def test_unsigned_short_field():
    field = fields.UnsignedShortField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-1)

    # 0 (min value)
    assert field.encode(0) == "\x00\x00"
    assert field.decode("\x00\x00") == 0

    # max value
    assert field.encode(65535) == "\xff\xff"
    assert field.decode("\xff\xff") == 65535

    # to high
    with pytest.raises(OverflowError):
        field.encode(65536)


def test_int_field():
    field = fields.IntField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-2147483648)

    # min value
    assert field.encode(-2147483647) == "\x80\x00\x00\x01"
    assert field.decode("\x80\x00\x00\x01") == -2147483647

    # 0
    assert field.encode(0) == "\x00\x00\x00\x00"
    assert field.decode("\x00\x00\x00\x00") == 0

    # max value
    assert field.encode(2147483647) == "\x7f\xff\xff\xff"
    assert field.decode("\x7f\xff\xff\xff") == 2147483647

    # to high
    with pytest.raises(OverflowError):
        field.encode(2147483648)


def test_long_long_field():
    field = fields.LongLongField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-9223372036854775808)

    # min value
    assert field.encode(-9223372036854775807) == "\x80\x00\x00\x00\x00\x00\x00\x01"
    assert field.decode("\x80\x00\x00\x00\x00\x00\x00\x01") == -9223372036854775807

    # 0
    assert field.encode(0) == "\x00\x00\x00\x00\x00\x00\x00\x00"
    assert field.decode("\x00\x00\x00\x00\x00\x00\x00\x00") == 0

    # max value
    assert field.encode(9223372036854775807) == "\x7f\xff\xff\xff\xff\xff\xff\xff"
    assert field.decode("\x7f\xff\xff\xff\xff\xff\xff\xff") == 9223372036854775807

    # too high
    with pytest.raises(OverflowError):
        field.encode(9223372036854775808)


def test_string_field():
    field = fields.StringField()

    # str
    assert field.encode("Hello !") == "\x00\x07Hello !"
    assert field.decode("\x00\x07Hello !") == "Hello !"

    # very long str
    long_str = (
        "wojfewjfwpejfjewofjwjfowefojwjfoewjofijewofjewojfeowjfowjfowejoifjewojfweoioifjowjowfjwjiwojoifjowfe"
        "fwjfweofhoiehwefoiegfurewgkwjenvoerbvoubreuwbverubwvuirbewuvibeiruwbvuierwbviuerbvubeuvibuebwviuruwe"
        "wojfewjfwpejfjewofjwjfowefojwjfoewjofijewofjewojfeowjfowjfowejoifjewojfweoioifjowjowfjwjiwojoifjowfe"
        "fwjfweofhoiehwefoiegfurewgkwjenvoerbvoubreuwbverubwvuirbewuvibeiruwbvuierwbviuerbvubeuvibuebwviuruwe"
    )
    encoded = field.encode(long_str)
    assert encoded[:2] == "\x01\x90"
    assert encoded[2:] == long_str
    assert field.decode("\x01\x90" + long_str) == long_str

    # unicode
    assert field.encode(u"ボールト") == "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    assert field.decode("\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88") == u"ボールト"


def test_float_field():
    field = fields.FloatField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-4 * pow(10, 38))

    # some very low value
    low_value = -3.2345678 * pow(10, 38)
    assert field.encode(low_value) == "\xff\x73\x57\x83"
    assert abs(field.decode("\xff\x73\x57\x83") - low_value) < abs(low_value * pow(10, -7))

    # still some negative value
    assert field.encode(-300) == "\xc3\x96\x00\x00"
    assert field.decode("\xc3\x96\x00\x00") == -300

    # 0
    assert field.encode(0) == "\x00\x00\x00\x00"
    assert field.decode("\x00\x00\x00\x00") == 0

    # some positive value
    assert field.encode(300) == "\x43\x96\x00\x00"
    assert field.decode("\x43\x96\x00\x00") == 300

    # some very high value
    high_value = 3.2345678 * pow(10, 38)
    assert field.encode(high_value) == "\x7f\x73\x57\x83"
    assert abs(field.decode("\x7f\x73\x57\x83") - high_value) < abs(high_value * pow(10, -7))


def test_double_field():
    field = fields.DoubleField()

    # too low
    with pytest.raises(OverflowError):
        field.encode(-4 * pow(10, 400))

    # some very low value
    low_value = -3.2345678 * pow(10, 64)
    assert field.encode(low_value) == "\xcd\x53\xa8\x30\xf3\x15\x89\x61"
    assert abs(field.decode("\xcd\x53\xa8\x30\xf3\x15\x89\x61") - low_value) < abs(low_value * pow(10, -8))

    # still some negative value
    assert field.encode(-300) == "\xc0\x72\xc0\x00\x00\x00\x00\x00"
    assert field.decode("\xc0\x72\xc0\x00\x00\x00\x00\x00") == -300

    # 0
    assert field.encode(0) == "\x00\x00\x00\x00\x00\x00\x00\x00"
    assert field.decode("\x00\x00\x00\x00\x00\x00\x00\x00") == 0

    # some positive value
    assert field.encode(300) == "\x40\x72\xc0\x00\x00\x00\x00\x00"
    assert field.decode("\x40\x72\xc0\x00\x00\x00\x00\x00") == 300

    # some very high value
    high_value = 3.2345678 * pow(10, 64)
    assert field.encode(high_value) == "\x4d\x53\xa8\x30\xf3\x15\x89\x61"
    assert abs(field.decode("\x4d\x53\xa8\x30\xf3\x15\x89\x61") - high_value) < abs(high_value * pow(10, -8))


options_field_data = [
    # split
    (dict(has_split=False, reliability=0x00), "\x00"),  # 0b00000000
    (dict(has_split=True, reliability=0x00), "\x10"),  # 0b00010000
    # reliability
    (dict(has_split=False, reliability=0x01), "\x20"),  # 0b00100000
    (dict(has_split=False, reliability=0x02), "\x40"),  # 0b01000000
    (dict(has_split=False, reliability=0x03), "\x60"),  # 0b01100000
    (dict(has_split=False, reliability=0x04), "\x80"),  # 0b10000000
    (dict(has_split=False, reliability=0x05), "\xa0"),  # 0b10100000
    (dict(has_split=False, reliability=0x06), "\xc0"),  # 0b11000000
    (dict(has_split=False, reliability=0x07), "\xe0"),  # 0b11100000
]


@pytest.mark.parametrize("decoded,encoded", options_field_data)
def test_options_field(encoded, decoded):
    field = fields.OptionsField()
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded


address_field_data = [
    (Address(ip="127.0.0.1", port=19132, version=4), "\x04\x7f\x00\x00\x01\x4a\xbc"),
    (Address(ip="192.168.0.42", port=29132, version=4), "\x04\xc0\xa8\x00\x2a\x71\xcc")
]


@pytest.mark.parametrize("decoded,encoded", address_field_data)
def test_address_field(encoded, decoded):
    field = fields.AddressField()
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded


range_list_field_data = [
    ([Range(min_index=0, max_index=0)], "\x00\x01\x01\x00\x00\x00"),
    ([Range(min_index=65536, max_index=327680)], "\x00\x01\x00\x01\x00\x00\x05\x00\x00"),
    ([Range(min_index=851968, max_index=917504)], "\x00\x01\x00\x0d\x00\x00\x0e\x00\x00"),
    ([Range(min_index=5373952, max_index=5373952), Range(min_index=7471104, max_index=7536640)],
        "\x00\x02\x01\x52\x00\x00\x00\x72\x00\x00\x73\x00\x00"),
    ([Range(min_index=9568256, max_index=9568256)], "\x00\x01\x01\x92\x00\x00"),
]


@pytest.mark.parametrize("decoded,encoded", range_list_field_data)
def test_range_list_field(encoded, decoded):
    field = fields.RangeListField()
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded


padding_field_data = [
    (0, 0, ""),
    (0, 1, "\x00"),
    (0, 5, "\x00\x00\x00\x00\x00"),
    (0, 20, "\x00" * 20),
    (0, 1500, "\x00" * 1500),
    (18, 18, ""),
    (18, 19, "\x00"),
    (18, 23, "\x00\x00\x00\x00\x00"),
    (18, 20, "\x00" * 2),
    (18, 1500, "\x00" * 1482),
]


@pytest.mark.parametrize("offset,decoded,encoded", padding_field_data)
def test_padding_field(offset, encoded, decoded):
    field = fields.PaddingField(offset=offset)
    assert field.encode(decoded) == encoded
    assert field.decode(encoded) == decoded
