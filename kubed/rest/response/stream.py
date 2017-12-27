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


RESPONSE_TIMEOUT_DEFAULT = 3


class StreamResponseBase(base.ResponseBase):
    """Parses and contains all information in response to a streamed request.
    """
    def __init__(self, request, response, **kwargs):
        base.ResponseBase.__init__(self, request, response)
        self.params = kwargs


class StreamResponseText(base.ResponseText):
    def __init__(self, request, response, **kwargs):
        base.ResponseText.__init__(self, request, response)
        self.params = kwargs


class StreamResponseJSON(base.ResponseJSON):
    def __init__(self, request, response, **kwargs):
        base.ResponseJSON.__init__(self, request, response)
        self.params = kwargs


class StreamResponseExec(StreamResponseText):
    def __init__(self, request, response, **kwargs):
        StreamResponseText.__init__(self, request, response, **kwargs)

    @property
    def interactive(self):
        return False

    @property
    def terminal(self):
        return bool(self.params.get('tty', False))


class StreamResponseInteractiveExec(StreamResponseExec):
    def __init__(self, request, streamer, **kwargs):
        StreamResponseExec.__init__(self, request, None, **kwargs)
        self.streamer = streamer

    @property
    def interactive(self):
        return True

    def close(self):
        self.streamer.close()

    def execute(self, command, timeout=RESPONSE_TIMEOUT_DEFAULT):
        if not self.streamer.is_open():
            # [todo] make custom error type for this
            raise RuntimeError('Stream: %s is not open', self.streamer)
        self.streamer.write_stdin(command + '\n')
        while not self.streamer.peek_stdout() or self.streamer.peek_stderr():
            time.sleep(1)

        return (
            self.streamer.read_stdout(timeout=timeout),
            self.streamer.read_stderr(timeout=timeout)
        )
