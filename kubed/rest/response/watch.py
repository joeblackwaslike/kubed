from . import base


class WatchResponse(base.ResponseJSON):
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

    def __init__(self, request, response, resource_version=None):
        # this will add .request, .resource, and .body (empty)
        base.ResponseJSON.__init__(self, request, None)
        self.events = response
        self.resource_version = resource_version

    def stream(self):
        for event in self.events:
            yield self.WatchEvent(
                self.request,
                event['type'],
                event['object'],
                event['raw_object']
            )

    def __iter__(self):
        return iter(self.stream)
