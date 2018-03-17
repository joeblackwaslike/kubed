"""
Kubed
==================
kubed.query.stream

[todo] Rewrite class and execute to stream stdin and stdout using
       generators/coroutines.
ref:   http://www.dabeaz.com/coroutines/Coroutines.pdf

Copyright 2017 Joe Black <me@joeblack.nyc>
"""
import time

import kubernetes

from . import base
from ...meta.decorators import lazy_property


_RESPONSE_TIMEOUT_DEFAULT = 3


class StreamResponseBase(base.ResponseBase):
    """Parses and contains all information in response to a streamed request.
    """
    def __init__(self, request, response, **kwargs):
        base.ResponseBase.__init__(self, request, response)
        self._params = kwargs


class StreamResponseText(base.ResponseText):
    def __init__(self, request, response, **kwargs):
        base.ResponseText.__init__(self, request, response)
        self._params = kwargs


class StreamResponseJSON(base.ResponseJSON):
    def __init__(self, request, response, **kwargs):
        base.ResponseJSON.__init__(self, request, response)
        self._params = kwargs


class StreamResponseExec(StreamResponseText):
    def __init__(self, request, response, **kwargs):
        StreamResponseText.__init__(self, request, response, **kwargs)

    @lazy_property
    def text(self):
        return self.body.strip()

    @property
    def interactive(self):
        return False

    @lazy_property
    def tty(self):
        return bool(self._params.get('tty'))


class StreamResponseInteractiveExec(StreamResponseExec):
    def __init__(self, request, streamer, **kwargs):
        StreamResponseExec.__init__(self, request, None, **kwargs)
        self._streamer = streamer

    @property
    def interactive(self):
        return True

    def close(self):
        self._streamer.close()

    def execute(self, command, timeout=_RESPONSE_TIMEOUT_DEFAULT):
        if not self._streamer.is_open():
            # [todo] make custom error type for this
            raise RuntimeError('Stream: %s is not open', self._streamer)
        self._streamer.write_stdin(command + '\n')
        while not self._streamer.peek_stdout() or self._streamer.peek_stderr():
            time.sleep(1)

        return (
            self._streamer.read_stdout(timeout=timeout),
            self._streamer.read_stderr(timeout=timeout)
        )
