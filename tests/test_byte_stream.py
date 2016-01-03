# -*- coding: utf-8 -*-
import os

from rakpy.io import ByteStream, convert_to_stream


def test_seek_set():
    data = "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    stream = ByteStream(data)
    assert stream.tell() == 0

    assert stream.seek(0) == 0
    assert stream.tell() == 0

    assert stream.seek(6) == 6
    assert stream.tell() == 6

    assert stream.seek(len(data)) == len(data)
    assert stream.tell() == len(data)

    assert stream.seek(len(data) + 42) == len(data)
    assert stream.tell() == len(data)


def test_seek_cur():
    data = "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    stream = ByteStream(data)
    assert stream.tell() == 0

    assert stream.seek(0, os.SEEK_CUR) == 0
    assert stream.tell() == 0

    assert stream.seek(3, os.SEEK_CUR) == 3
    assert stream.tell() == 3

    assert stream.seek(3, os.SEEK_CUR) == 6
    assert stream.tell() == 6

    assert stream.seek(128) == len(data)
    assert stream.tell() == len(data)


def test_seek_end():
    data = "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    stream = ByteStream(data)
    assert stream.tell() == 0

    assert stream.seek(0, os.SEEK_END) == len(data)
    assert stream.tell() == len(data)

    assert stream.seek(42, os.SEEK_END) == len(data)
    assert stream.tell() == len(data)

    assert stream.seek(-5, os.SEEK_END) == len(data) - 5
    assert stream.tell() == len(data) - 5


def test_read_all():
    data = "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    stream = ByteStream(data)
    assert stream.tell() == 0

    assert stream.readall() == data
    assert stream.tell() == len(data)

    assert stream.seek(6) == 6
    assert stream.readall() == data[6:]
    assert stream.tell() == len(data)


def test_read():
    data = "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    stream = ByteStream(data)
    assert stream.tell() == 0

    assert stream.read() == data
    assert stream.tell() == len(data)

    # read 0 bytes
    assert stream.seek(0) == 0
    assert stream.read(0) == ""
    assert stream.tell() == 0

    # read 1 byte
    assert stream.seek(0) == 0
    for i in range(len(data)):
        assert stream.read(1) == data[i:i+1]
        assert stream.tell() == i + 1

    # read 3 bytes
    assert stream.seek(0) == 0
    for i in range(0, len(data), 3):
        assert stream.read(3) == data[i:i+3]
        assert stream.tell() == min(i + 3, len(data))


def test_slice():
    data = "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    stream = ByteStream(data)
    assert stream.tell() == 0

    assert stream[0] == data[0]
    assert stream[5] == data[5]
    assert stream[5:] == data[5:]
    assert stream[:5] == data[:5]
    assert stream[3:5] == data[3:5]
    assert stream[-5] == data[-5]
    assert stream[-5:] == data[-5:]


def test_len():
    data = "\x00\x0c\xe3\x83\x9c\xe3\x83\xbc\xe3\x83\xab\xe3\x83\x88"
    stream = ByteStream(data)
    assert stream.tell() == 0

    # read 1 byte
    assert stream.seek(0) == 0
    assert len(stream) == len(data)
    expected_length = len(data)
    for i in range(len(data)):
        read = stream.read(1)
        expected_length -= len(read)
        assert len(stream) == expected_length

    # read 3 byte
    assert stream.seek(0) == 0
    assert len(stream) == len(data)
    expected_length = len(data)
    for i in range(0, len(data), 3):
        read = stream.read(3)
        expected_length -= len(read)
        assert len(stream) == expected_length


def test_convert_to_stream():

    class TestHelper(object):

        @convert_to_stream("data")
        def test(self, data):
            return data

        @convert_to_stream("foo")
        def test_invalid(self, bar):
            return bar

    data = "\x01\x02\x03\x04\x05"

    helper = TestHelper()

    stream = helper.test(data)
    assert type(stream) == ByteStream
    assert stream.readall() == data

    # argument name mismatch
    stream = helper.test_invalid(data)
    assert stream == data
