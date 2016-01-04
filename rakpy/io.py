# -*- coding: utf-8 -*-
import os


class EndOfStreamException(Exception):
    pass


class ByteStream(object):

    def __init__(self, data):
        self._buffer = memoryview(data)
        self._offset = 0

    def read(self, size=-1):
        if size == 0:
            return ""
        elif size < 0:
            return self.readall()
        else:
            offset = self._offset
            self.seek(size, os.SEEK_CUR)
            data = self._buffer[offset:offset+size].tobytes()
            if not len(data):
                raise EndOfStreamException()
            return data

    def readall(self):
        offset = self._offset
        self.seek(0, os.SEEK_END)
        return self._buffer[offset:].tobytes()

    def seekable(self):
        return True

    def seek(self, offset, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._offset = offset
        elif whence == os.SEEK_CUR:
            self._offset += offset
        elif whence == os.SEEK_END:
            self._offset = len(self._buffer) + offset
        self._offset = min(self._offset, len(self._buffer))
        return self._offset

    def tell(self):
        return self._offset

    def __getitem__(self, item):
        return self._buffer.__getitem__(item)

    def __len__(self):
        return len(self._buffer[self._offset:])


def convert_to_stream(argument_name):
    def actual_decorator(function):
        try:
            argument_index = function.func_code.co_varnames.index(argument_name)
        except ValueError:
            return function

        def wrapper(*args, **kwargs):
            try:
                args[argument_index].seekable()
            except AttributeError:
                args = args[:argument_index] + (ByteStream(args[argument_index]),) + args[argument_index+1:]
            return function(*args, **kwargs)
        return wrapper
    return actual_decorator
