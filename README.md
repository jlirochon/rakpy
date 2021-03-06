# rakpy

Pythonic implementation of the [RakNet](https://github.com/OculusVR/RakNet) protocol **WORK IN PROGRESS**

## Status

[![Build Status](https://img.shields.io/travis/jlirochon/rakpy/master.svg?style=flat-square)](https://travis-ci.org/jlirochon/rakpy)
[![Code Coverage](https://img.shields.io/codecov/c/github/jlirochon/rakpy/master.svg?style=flat-square)](https://codecov.io/github/jlirochon/rakpy?branch=master)
[![Code Quality](https://img.shields.io/codacy/921c9b1c67c34a3f824382737634bbd4.svg?style=flat-square)](https://www.codacy.com/app/julien_6/rakpy)
[![Chat](https://img.shields.io/gitter/room/jlirochon/rakpy.svg?style=flat-square)](https://gitter.im/jlirochon/rakpy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

## Compatibility

![Python 3.5, 3.4, 3.3](https://img.shields.io/badge/Python-3.5,%203.4,%203.3-blue.svg?style=flat-square)
![Python 2.7](https://img.shields.io/badge/Python-2.7-blue.svg?style=flat-square)

## Project goals

* Provide a pythonic interface (other projects exist but they feel like Java or PHP)
* Provide a decent test suite
* Parts of the code are generated from YAML files (so we can move fast by tweaking YAML, and we can share this with other projects)
* Cover enough to implement a MCPE server

## Usage

### Decoding packets

```python
In [1]: from rakpy.protocol import decode_packet

In [2]: buffer = b"\x01\x00\ (...) \x23\xa3"  # data from UDP packet

In [3]: packet = decode_packet(buffer)

In [4]: print packet
UnconnectedPing(time=193351, client_guid=1450258689827747)

In [5]: packet.time
193351

In [6]: packet.client_guid
1450258689827747
```

### Encoding packets (not implemented yet)

```python
In [1]: from rakpy.protocol.packets import UnconnectedPing

In [2]: packet = UnconnectedPong(ping_time=193351, server_guid=1450258689827742)

In [3]: packet.encode()
b"\x1c\x00\ (...) \x23\xa3"  # you can send this over UDP
```
