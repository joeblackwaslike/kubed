from copy import copy

from .api.bases import APIObjectBase
from .. import rest, strutil
from ..rest.constants import NAMESPACE_DEFAULT


class _APIObjectManager:
    def __init__(self, client, resource):
        self.client = client
        self.resource = resource
        self.api = client.api_for(resource)

    @property
    def namespace(self):
        return self.client.namespace

    def manager_for(self, kind):
        resource = APIObjectBase.resource_for(kind)
        return type(self)(self.client, resource)

    # kwargs: name, selectors=dict(label=dict(app='couchdb'), field={'metadata.name': 'couchdb'})
    def get(self, namespace=NAMESPACE_DEFAULT, **kwargs):
        request = rest.Request(
            self.clone(),
            'get',
            namespace=namespace,
            **kwargs
        )
        return request.execute()

    def create(self, obj=None, namespace=NAMESPACE_DEFAULT, **kwargs):
        request = rest.Request(
            self.clone(),
            'create',
            namespace=namespace,
            body=obj,
            **kwargs
        )
        return request.execute()

    # same args as get above plus version and timeout
    def watch(self, namespace=NAMESPACE_DEFAULT, resource_version=0,
              timeout=None, **kwargs):
        request = rest.WatchRequest(
            self.clone(),
            'get',
            namespace=namespace,
            resource_version=resource_version,
            timeout=timeout,
            **kwargs
        )
        return request.execute()

    def clone(self):
        # [todo] implement a custom copy that performs deepcopy without
        # `can't pickle thread.Rlock` error
        return type(self)(self.client, self.resource)

    def __repr__(self):
        return f'{type(self).__name__}(namepace: {self.namespace})'
