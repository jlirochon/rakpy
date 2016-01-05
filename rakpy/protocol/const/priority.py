# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# The highest possible priority. These message trigger sends immediately, and are generally not buffered or
# aggregated into a single datagram.
IMMEDIATE_PRIORITY = 0x00

# For every 2 IMMEDIATE_PRIORITY messages, 1 HIGH_PRIORITY will be sent.
# Messages at this priority and lower are buffered to be sent in groups at 10 millisecond intervals to reduce UDP
# overhead and better measure congestion control.
HIGH_PRIORITY = 0x01

# For every 2 HIGH_PRIORITY messages, 1 MEDIUM_PRIORITY will be sent.
# Messages at this priority and lower are buffered to be sent in groups at 10 millisecond intervals to reduce UDP
# overhead and better measure congestion control.
MEDIUM_PRIORITY = 0x02

# For every 2 MEDIUM_PRIORITY messages, 1 LOW_PRIORITY will be sent.
# Messages at this priority and lower are buffered to be sent in groups at 10 millisecond intervals to reduce UDP
# overhead and better measure congestion control.
LOW_PRIORITY = 0x03
