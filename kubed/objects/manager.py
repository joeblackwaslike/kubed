from copy import copy

from .. import rest
from .api.bases import APIObjectBase
from .. import strutil


class _APIObjectManager:
    def __init__(self, client, resource):
        self.client = client
        self.resource = resource
        self.api = client.api_for(resource)

    @property
    def namespace(self):
        return self.client.namespace

    @classmethod
    def manager_for(cls, kind):
        resource = APIObjectBase.resource_for(kind)
        return cls(client, resource)

    # kwargs: name, filters=dict(label={filter}, field={filter}), watch, resource_version
    def get(self, namespace=None, **kwargs):
        request = rest.request(
            self.clone(),
            'get',
            namespace=namespace,
            **kwargs
        )
        return request.execute()

    def create(self, obj=None, namespace=None, **kwargs):
        request = rest.request(
            self.clone(),
            'create',
            namespace=namespace,
            body=obj,
            **kwargs
        )
        return request.execute()

    def clone(self):
        # [todo] implement a custom copy that performs deepcopy without
        # `can't pickle thread.Rlock` error
        return type(self)(self.client, self.resource)

    def __repr__(self):
        return f'{type(self).__name__}(namepace: {self.namespace})'
