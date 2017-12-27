import kubernetes

from . import openapi
from .. import response
from ..constants import NAMESPACE_DEFAULT


class Request:
    """Contains all information and logic for executing an API Request.
    """
    def __init__(self, manager, action, namespace=NAMESPACE_DEFAULT, **kwargs):
        self.manager = manager
        self.action = action
        self.resource = manager.resource
        self.api = manager.api

        self.params = openapi.params(self, manager, namespace, **kwargs)
        self.method = openapi.method(self, action, self.resource)

    @property
    def watched(self):
        return self.params.watched

    @property
    def namespaced(self):
        return self.params.namespaced

    @property
    def named(self):
        return self.params.named

    @property
    def streamed(self):
        return self.params.streamed

    def execute(self):
        params = self.params.build()
        return response.respond(self, **params)
