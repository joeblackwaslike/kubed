from copy import deepcopy

import kubernetes

from . import apis
from .context import ClientContext
from .. import objects
from ..meta import pattern
from ..objects.manager import _APIObjectManager
from ..objects.api.bases import CustomObjectBase


class APIClient(pattern.Proxy):
    # _custom_objects = dict()
    def __init__(self, context=None, **kwargs):
        client_context = context or ClientContext(**kwargs)
        pattern.Proxy.__init__(self, client_context.client)
        self._context = client_context
        self._apis = apis._KubeAPIs(self)
        # attach a reference to models so we can build objects using models
        self.models = kubernetes.client.models

        self.namespaces = _APIObjectManager(self, objects.Namespace)
        self.nodes = _APIObjectManager(self, objects.Node)
        self.pods = _APIObjectManager(self, objects.Pod)
        self.config_maps = _APIObjectManager(self, objects.ConfigMap)
        self.secrets = _APIObjectManager(self, objects.Secret)
        self.endpoints = _APIObjectManager(self, objects.Endpoints)
        self.services = _APIObjectManager(self, objects.Service)
        self.ingresses = _APIObjectManager(self, objects.Ingress)
        self.replica_sets = _APIObjectManager(self, objects.ReplicaSet)
        self.daemon_sets = _APIObjectManager(self, objects.DaemonSet)
        self.deployments = _APIObjectManager(self, objects.Deployment)
        self.stateful_sets = _APIObjectManager(self, objects.StatefulSet)
        self.jobs = _APIObjectManager(self, objects.Job)
        self.cron_jobs = _APIObjectManager(self, objects.Job)
        self.persistent_volumes = _APIObjectManager(
            self, objects.PersistentVolume)
        self.persistent_volume_claims = _APIObjectManager(
            self, objects.PersistentVolumeClaim)
        self.service_accounts = _APIObjectManager(self, objects.ServiceAccount)
        self.custom_resource_definitions = _APIObjectManager(
            self, objects.CustomResourceDefinition)

        # for key, val in self._custom_objects.items():
        #     setattr(self, key, _APIObjectManager(self, val))

        for name, class_ in CustomObjectBase.custom_objects():
            setattr(self, name, _APIObjectManager(self, class_))


    @classmethod
    def register_custom_object(self, plural, resource):
        self._custom_objects[plural] = resource

    def clone(self):
        return type(self)(context=self._context)

    def manager_for(self, kind):
        return _APIObjectManager.manager_for(self, kind)

    def api_for(self, resource):
        return self._apis[resource._api_group]

    @classmethod
    def from_config(cls, context=None):
        new_client = kubernetes.config.new_client_from_config(context=context)
        new_context = KubedContext(client=new_client)
        return cls(context=new_context)

    @property
    def namespace(self):
        return (
            self._wrapped.configuration.namespace or
            self.configuration.namespace
        )
    @property
    def host(self):
        return getattr(self.configuration, 'host', None)

    @property
    def kind(self):
        config_class_name = type(self.configuration).__name__
        if 'KubeConfig' in config_class_name:
            return 'kubeconfig'
        return 'incluster'

    def __repr__(self):
        class_name = type(self).__name__
        kind = self.kind
        details = self.host
        if self.namespace:
            details += '/' + self.namespace
        return f'{class_name}({kind}: {details})'
