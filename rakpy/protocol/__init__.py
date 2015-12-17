# -*- coding: utf-8 -*-
import inspect

import six

from rakpy.protocol.const import MAGIC
from rakpy.protocol.exceptions import UnknownPacketException, RemainingDataException
from rakpy.protocol.fields import Field


class PacketRegistry(dict):
    def __init__(self):
        super(PacketRegistry, self).__init__()

    def add(self, decorated_class):
        """
        @add decorator
        :param decorated_class:
        """
        id = decorated_class._meta.id
        if dict.__contains__(self, id):
            raise ValueError("Packet with id={} aldready registered")
        dict.__setitem__(self, id, decorated_class)
        return decorated_class
registry = PacketRegistry()


def decode_packet(data):
    try:
        packet_class = registry[ord(data[:1])]
    except KeyError:
        raise UnknownPacketException
    return packet_class(data)


class Options(object):
    def __init__(self, meta):
        self.id = meta.id
        self.structure = meta.structure
        self.fields = dict()

    def add_field(self, field, name):
        self.fields[name] = field


class PacketBase(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super(PacketBase, mcs).__new__

        # Ensure initialization is only performed for subclasses of Packet
        # (excluding Packet class itself).
        parents = [b for b in bases if isinstance(b, PacketBase)]
        if not parents:
            return super_new(mcs, name, bases, attributes)

        module = attributes.pop('__module__')
        new_class = super_new(mcs, name, bases, {'__module__': module})

        # Add meta
        meta = attributes.pop('Meta')
        new_class.add_to_class("_meta", Options(meta))

        # Add remaining attributes (fields are added here)
        for obj_name, obj in attributes.items():
            new_class.add_to_class(obj_name, obj)

        return new_class

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Packet(six.with_metaclass(PacketBase)):

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            self._decode(args[0])
        super(Packet, self).__init__()

    def _get_id(self):
        return self._meta.id
    id = property(_get_id)

    def _decode(self, data):
        if self._meta.id != ord(data[0]):
            raise ValueError

        # drop first byte
        data = data[1:]

        for name in self._meta.structure:
            if name == "__magic__":
                field = MagicField()
                length = field.guess_length(data)
            else:
                field = self._meta.fields[name]
                length = field.guess_length(data)
                setattr(self, name, field.decode(data[:length]))
            data = data[length:]
        if len(data):
            raise RemainingDataException(data)

    def __repr__(self):
        values = ("=".join([field_name, str(getattr(self, field_name))])
                  for field_name in self._meta.structure if field_name != "__magic__")
        return "{}({})".format(type(self).__name__, ", ".join(values))


class MagicField(Field):
    def guess_length(self, data):
        return len(MAGIC)

    def decode(self, data):
        raise NotImplementedError()

    def encode(self, value):
        return MAGIC


from rakpy.protocol.packets import *
