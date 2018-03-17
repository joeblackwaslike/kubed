import urllib3

from . import transforms
from ..constants import TRANSFORMS_DEFAULT
from ...exceptions import NoPodsFoundError


class ResponseBase:
    def __init__(self, request, body):
        self.request = request
        self._resource = request.resource
        self._manager = request.manager

    @property
    def namespace(self):
        return self.request.params.namespace

    def __repr__(self):
        class_name = type(self).__name__
        resource_name = self._resource.__name__
        return f'{class_name}(resource: {resource_name})'


class ResponseText(ResponseBase):
    def __init__(self, request, body):
        ResponseBase.__init__(self, request, body)
        self.body = body

    @property
    def streaming(self):
        return isinstance(self.body, urllib3.response.HTTPResponse)

    @property
    def text(self):
        if self.streaming:
            return self.body.read().strip()
        return self.body.strip()

    def __iter__(self):
        if self.streaming:
            return iter(self.body.stream())
        return iter(self.text.splitlines())

    def __len__(self):
        return len(self.text.splitlines())


class ResponseJSON(ResponseBase):
    """Parses and contains all information in response to an API request.
    """

    def __init__(self, request, body):
        ResponseBase.__init__(self, request, body)
        if body:
            self.raw = body
            if isinstance(body, dict):
                if 'items' in body:
                    body = body['items']
            elif hasattr(body, 'items'):
                body = body.items or []
            else:
                body = [body]

            if not len(body):
                raise NoPodsFoundError('No pods found matching criteria!')
            self.body = body

            for name in self._resource._transforms:
                transform = transforms.TransformBase.get_transform(name)
                transform(self).apply()

    def first(self, count=1):
        if count == 1:
            return self.body[0]
        return self.body[0:count]

    def all(self):
        return self.body
