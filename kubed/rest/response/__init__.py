import kubernetes

from . import transforms, base, watch, stream
from .base import ResponseText, ResponseJSON
from .watch import WatchResponse
from .stream import (
    StreamResponseText,
    StreamResponseJSON,
    StreamResponseExec,
    StreamResponseInteractiveExec
)



# def respond(request, **kwargs):
    # if request.watched:
    #     wobj = kubernetes.watch.Watch()
    #     response = wobj.stream(request.method.ref, **request.params.watch)
    #     return watch.WatchResponse(request, response, **kwargs)

    # elif request.streamed:
    #     response = kubernetes.stream.stream(request.method.ref, **kwargs)
    #     if request.action == 'exec':
    #         if kwargs.get('stdin'):
    #             return stream.StreamResponseInteractiveExec(
    #                 request, response, **kwargs)
    #         return stream.StreamResponseExec(request, response, **kwargs)
    #
    #     elif isinstance(response, str):
    #         return stream.StreamResponseText(request, response, **kwargs)
    #     return stream.StreamResponseJSON(request, response, **kwargs)

    # else:
    #     response = request.method(**kwargs)
    #     if isinstance(response, str):
    #         return base.ResponseText(request, response)
    #     return base.ResponseJSON(request, response)
