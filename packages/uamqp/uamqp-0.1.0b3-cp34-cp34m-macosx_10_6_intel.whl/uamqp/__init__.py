#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys

from uamqp import c_uamqp
from uamqp.message import Message, BatchMessage
from uamqp.address import Source, Target

from uamqp.connection import Connection
from uamqp.session import Session
from uamqp.client import AMQPClient, SendClient, ReceiveClient
from uamqp.sender import MessageSender
from uamqp.receiver import MessageReceiver

try:
    from uamqp.async import ConnectionAsync
    from uamqp.async import SessionAsync
    from uamqp.async import MessageSenderAsync
    from uamqp.async import MessageReceiverAsync
    from uamqp.async import AMQPClientAsync, SendClientAsync, ReceiveClientAsync
except (SyntaxError, ImportError):
    pass  # Async not supported.


__version__ = "0.1.0b3"


_logger = logging.getLogger(__name__)
_is_win = sys.platform.startswith('win')
c_uamqp.set_python_logger()


def send_message(target, data, auth=None, debug=False):
    message = data if isinstance(data, Message) else Message(data)
    with SendClient(target, auth=auth, debug=debug) as send_client:
        send_client.queue_message(message)
        send_client.send_all_messages()


def receive_message(source, auth=None, timeout=0, debug=False):
    received = receive_messages(source, auth=auth, max_batch_size=1, timeout=timeout, debug=debug)
    if received:
        return received[0]
    else:
        return None


def receive_messages(source, auth=None, max_batch_size=None, timeout=0, debug=False, **kwargs):
    if max_batch_size:
        kwargs['prefetch'] = max_batch_size
    with ReceiveClient(source, auth=auth, debug=debug, **kwargs) as receive_client:
        print("receiving batch", max_batch_size)
        return receive_client.receive_message_batch(
            max_batch_size=max_batch_size or receive_client._prefetch, timeout=timeout)


class _Platform:

    initialized = False

    @classmethod
    def initialize(cls):
        if cls.initialized:
            _logger.debug("Platform already initialized.")
        else:
            _logger.debug("Initializing platform.")
            c_uamqp.platform_init()
            cls.initialized = True

    @classmethod
    def deinitialize(cls):
        if not cls.initialized:
           _logger.debug("Platform already deinitialized.")
        else:
            cls.initialized = False
            _logger.debug("Deinitializing platform.")
            c_uamqp.platform_deinit()


def get_platform_info(self):
    return str(c_uamqp.get_info())
