from .base import ResponseJSON


class WatchResponse(ResponseJSON):
    """Parses and contains all information in response to a Watch Request.
    """
    class WatchEvent:
        """Contains the event kind and object for each Watch Query Event.
        """
        def __init__(self, request, type_, obj, raw=None):
            resource = request.resource
            self.type = type_.lower()
            self.obj = resource(request.manager, obj)
            self.raw = raw

        def __repr__(self):
            class_name = type(self).__name__
            return f'{class_name}({self.type} {self.obj})'

    def __init__(self, request, response, **kwargs):
        # this will add .request, .resource
        ResponseJSON.__init__(self, request, body=None)
        self._events = response  # the response on a watch request are events
        self.resource_version = kwargs.pop('resource_version', None)
        self.timeout = kwargs.pop('timeout_seconds', None)

    def stream(self):
        for event in self._events:
            yield self.WatchEvent(
                self.request,
                event['type'],
                event['object'],
                event['raw_object']
            )

    def __iter__(self):
        return iter(self.stream)

    def __repr__(self):
        class_name = type(self).__name__
        return f'{class_name}({self.resource})'
