import urllib3
import kubernetes

from . import openapi
from ..constants import NAMESPACE_DEFAULT
from ..response import (
    ResponseText,
    ResponseJSON,
    WatchResponse,
    StreamResponseText,
    StreamResponseJSON,
    StreamResponseExec,
    StreamResponseInteractiveExec
)


class Request:
    """Contains all information and logic for executing an API Request.
    """
    def __init__(self, manager, action, namespace=None, **kwargs):
        self.manager = manager
        self.action = action
        self.resource = manager.resource
        self.api = manager.api

        self.params = openapi._RequestParams(self, manager, namespace, **kwargs)
        self.method = openapi._RequestMethod(self, action, self.resource)

    @property
    def watched(self):
        return False

    @property
    def streamed(self):
        return False

    @property
    def namespaced(self):
        return self.params.namespaced

    @property
    def by_name(self):
        return bool(self.params.name)

    def execute(self):
        params = self.params.build()
        response = self.method(**params)
        if isinstance(response, (str, urllib3.response.HTTPResponse)):
            return ResponseText(self, response)
        return ResponseJSON(self, response)


class WatchRequest(Request):
    def __init__(self, *args, resource_version=0, timeout=None, **kwargs):
        Request.__init__(self, *args, **kwargs)
        self.params.watch = dict(
            resource_version=resource_version,
            timeout_seconds=timeout
        )

    @property
    def watched(self):
        return True

    def execute(self):
        params = self.params.build()
        wobj = kubernetes.watch.Watch()
        response = wobj.stream(self.method.ref, **params, **self.params.watch)
        return WatchResponse(self, response, **self.params.watch)


class StreamRequest(Request):
    def __init__(self, *args, timeout=None, **kwargs):
        Request.__init__(self, *args, **kwargs)
        self.params.stream = dict(timeout=timeout)

    @property
    def streamed(self):
        return True

    @property
    def interactive(self):
        return self.params.build().get('stdin', False)

    def execute(self):
        params = self.params.build()
        response = kubernetes.stream.stream(self.method.ref, **params)
        if self.action == 'exec':
            if self.interactive:
                return StreamResponseInteractiveExec(self, response, **params)
            return StreamResponseExec(self, response, **params)
        elif isinstance(response, str):
            return StreamResponseText(self, response, **params)
        return StreamResponseJSON(self, response, **params)
