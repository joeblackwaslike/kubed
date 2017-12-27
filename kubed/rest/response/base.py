from . import transforms
from ..constants import TRANSFORMS_DEFAULT
from ...exceptions import NoPodsFoundError


class ResponseBase:
    def __init__(self, request, body):
        self.request = request
        self.resource = request.resource
        self.manager = request.manager

    @property
    def namespace(self):
        return self.request.params.namespace

    def __repr__(self):
        class_name = type(self).__name__
        resource_name = self.resource.__name__
        return f'{class_name}(resource: {resource_name})'


class ResponseText(ResponseBase):
    def __init__(self, request, body):
        ResponseBase.__init__(self, request, body)
        self.body = body

    def __iter__(self):
        return iter(self.body.splitlines())

    def __len__(self):
        return len(self.body.splitlines())


class ResponseJSON(ResponseBase):
    """Parses and contains all information in response to an API request.
    """

    def __init__(self, request, body):
        ResponseBase.__init__(self, request, body)
        if body:
            self.raw = body
            if hasattr(body, 'items'):
                if not body.items:
                    raise NoPodsFoundError('No pods found matching criteria!')
                self.body = body.items
            else:
                self.body = [body]

            for name in self.transforms:
                transform = transforms.TransformBase.transform_for(name)
                transform(self).apply()

    @property
    def transforms(self):
        transforms_ = list(TRANSFORMS_DEFAULT)
        transforms_.append('MissingFieldCopier')
        if getattr(self.resource, '_transforms', None):
            transforms_.extend(list(self.resource._transforms))
        return transforms_

    def first(self, count=1):
        if count == 1:
            return self.body[0]
        return self.body[0:count]

    def all(self):
        return self.body

    def watch(self, version=None, timeout=None):
        kwargs = dict()
        if version:
            kwargs['resource_version'] = version
        if timeout:
            kwargs['timeout_seconds'] = timeout

        request = self.request
        request.params._watched = True
        request.params.params.update(kwargs)
        return request.execute()
