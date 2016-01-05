# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# Same as regular UDP, except that it will also discard duplicate datagrams.
# RakNet adds (6 to 17) + 21 bits of overhead, 16 of which is used to detect duplicate packets
# and 6 to 17 of which is used for message length.
UNRELIABLE = 0x00
# Regular UDP with a sequence counter. Out of order messages will be discarded.
# Sequenced and ordered messages sent on the same channel will arrive in the order sent.
UNRELIABLE_SEQUENCED = 0x01
# The message is sent reliably, but not necessarily in any order.  Same overhead as UNRELIABLE.
RELIABLE = 0x02
# This message is reliable and will arrive in the order you sent it.
# Messages will be delayed while waiting for out of order messages.
# Same overhead as UNRELIABLE_SEQUENCED.
RELIABLE_ORDERED = 0x03
# This message is reliable and will arrive in the sequence you sent it.
# Out or order messages will be dropped.  Same overhead as UNRELIABLE_SEQUENCED.
RELIABLE_SEQUENCED = 0x04
# Same as UNRELIABLE, however the user will get either ID_SND_RECEIPT_ACKED or ID_SND_RECEIPT_LOSS based on the
# result of sending this message when calling RakPeerInterface::Receive().
# Bytes 1-4 will contain the number returned from the Send() function.
# On disconnect or shutdown, all messages not previously acked should be considered lost.
UNRELIABLE_WITH_ACK_RECEIPT = 0x05
# Same as RELIABLE. The user will also get ID_SND_RECEIPT_ACKED after the message is delivered when calling
# RakPeerInterface::Receive(). ID_SND_RECEIPT_ACKED is returned when the message arrives, not necessarily the
# order when it was sent.
# Bytes 1-4 will contain the number returned from the Send() function.
# On disconnect or shutdown, all messages not previously acked should be considered lost.
# This does not return ID_SND_RECEIPT_LOSS.
RELIABLE_WITH_ACK_RECEIPT = 0x06
# Same as RELIABLE_ORDERED_ACK_RECEIPT. The user will also get ID_SND_RECEIPT_ACKED after the message is
# delivered when calling RakPeerInterface::Receive().
# ID_SND_RECEIPT_ACKED is returned when the message arrives, not necessarily the order when it was sent.
# Bytes 1-4 will contain the number returned from the Send() function.
# On disconnect or shutdown, all messages not previously acked should be considered lost.
# This does not return ID_SND_RECEIPT_LOSS.
RELIABLE_ORDERED_WITH_ACK_RECEIPT = 0x07


def is_reliable(reliability):
    return reliability in (
        RELIABLE,
        RELIABLE_ORDERED,
        RELIABLE_SEQUENCED,
        RELIABLE_WITH_ACK_RECEIPT,
        RELIABLE_ORDERED_WITH_ACK_RECEIPT
    )


def is_ordered(reliability):
    return reliability not in (UNRELIABLE, RELIABLE) and reliability <= RELIABLE_SEQUENCED
