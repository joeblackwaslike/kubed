# from os.path import dirname, join, abspath
# import sys
#
# this_dir = abspath(join(__file__, '..', '..'))
# sys.path.insert(0, this_dir)

import os
import logging

# import kubernetes
# from kubernetes.client.rest import ApiException

# import kubed
from kubed import ClientContext, APIClient
import time

DEBUG = False

if DEBUG:
    os.putenv('KUBE_DEBUG', 'true')
    logging.basicConfig(level=logging.DEBUG)


from kubed.objects.api.bases import CustomObjectBase
from kubed.objects.api.groups import CustomAPIGroupBase
from kubed.client.apis import CustomObjectAPI
from kubed.objects.api.properties import Namespaced

from kubernetes.client.apis.custom_objects_api import CustomObjectsApi
from kubernetes.client import V1DeleteOptions


class CustomObjectMixin:
    _namespaced = False
    def _create(self, body, **kwargs):
        return self._api.create_cluster_custom_object(
            group=self._api_group,
            version=self.version,
            plural=self._plural_name,
            body=body,
            **kwargs
        )

    def _get(self, name, **kwargs):
        return self._api.get_cluster_custom_object(
            group=self._api_group,
            version=self.version,
            plural=self._plural_name,
            name=name,
            **kwargs
        )

    def _list(self, **kwargs):
        return self._api.list_cluster_custom_object(
            group=self._api_group,
            version=self.version,
            plural=self._plural_name,
            **kwargs
        )

    def _replace(self, name, body, **kwargs):
        return self._api.replace_cluster_custom_object(
            group=self._api_group,
            version=self.version,
            plural=self._plural_name,
            name=name,
            body=body,
            **kwargs
        )

    def _delete(self, name, options, *args, **kwargs):
        return self._api.delete_cluster_custom_object(
            group=self._api_group,
            version=self.version,
            plural=self._plural_name,
            name=name,
            body=V1DeleteOptions(**options),
            **kwargs
        )


class NamespacedCustomObjectMixin:
    _namespaced = True
    def _create(self, namespace, body, **kwargs):
        return self._api.create_namespaced_custom_object(
            group=self._api_group,
            version=self.version,
            namespace=namespace,
            body=body,
            **kwargs
        )

    def _get(self, namespace, name, **kwargs):
        return self._api.get_namespaced_custom_object(
            group=self._api_group,
            version=self.version,
            namespace=namespace,
            name=name,
            **kwargs
        )

    def _list(self, namespace, **kwargs):
        return self._api.list_namespaced_custom_object(
            group=self._api_group,
            version=self.version,
            namespace=namespace,
            **kwargs
        )

    def _replace(self, namespace, name, body, **kwargs):
        return self._api.replace_namespaced_custom_object(
            group=self._api_group,
            version=self.version,
            namespace=namespace,
            name=name,
            body=body,
            **kwargs
        )

    def _delete(self, namespace, name, options, *args, **kwargs):
        return self._api.delete_namespaced_custom_object(
            group=self._api_group,
            version=self.version,
            namespace=namespace,
            name=name,
            body=V1DeleteOptions(**options),
            **kwargs
        )


class RookIOClusterAPI(CustomObjectAPI, NamespacedCustomObjectMixin):
    _api_group = 'rook.io'
    _plural_name = 'clusters'

    def create_namespaced_cluster(self, *args, **kwargs):
        return self._create(*args, plural=self._plural_name, **kwargs)

    def read_namespaced_cluster(self, *args, **kwargs):
        return self._get(*args, plural=self._plural_name, **kwargs)

    def list_namespaced_cluster(self, *args, **kwargs):
        return self._list(*args, plural=self._plural_name, **kwargs)

    def replace_namespaced_cluster(self, *args, **kwargs):
        return self._replace(*args, plural=self._plural_name, **kwargs)

    def delete_namespaced_cluster(self, *args, **kwargs):
        return self._delete(*args, plural=self._plural_name, **kwargs)


class RookIOAPIGroup(CustomAPIGroupBase):
    _api_group = 'rook.io'


class Cluster(Namespaced, CustomObjectBase, RookIOAPIGroup):
    _plural_name = 'clusters'
    def __init__(self, *args, **kwargs):
        CustomObjectBase.__init__(self, *args, **kwargs)


client = APIClient()

clusters = client.clusters.get(namespace='rook').all()
cluster = client.clusters.get(namespace='rook').first()

pods = client.pods.get(namespace='default').all()
pod = client.pods.get(namespace='default').first()

client._apis.get('rook.io')




# from datetime import timedelta
# print('testing pod logs')
# pod = client.pods.get(selectors=dict(label=dict(app='couchdb'))).first()
# logs = pod.logs(container='couchdb', since=timedelta(minutes=10))
#
# logs = pod.logs(container='couchdb', follow=True, since=timedelta(minutes=10), tail=5)
# assert getattr(logs, 'body', None)
# assert len(logs.body.splitlines()) > 100

# print('testing watch')
# pod_watch = client.pods.watch(timeout=5)
# events = [event for event in pod_watch.stream()]
# assert isinstance(events, list)
# assert len(events) > 32
#
#
# print('testing watch event')
# event = events[0]
# assert isinstance(event, kubed.rest.response.watch.WatchResponse.WatchEvent)
# assert event.type in ('added', 'updated', 'deleted')
# assert isinstance(event.obj, kubed.objects.api.resources.Pod)
# assert isinstance(event.raw, dict)


# pod = client.pods.get(name='busybox', namespace='default').first()
# pod.exec(command='echo hello > ~/.hello', shell='/bin/ash')
# response = pod.exec(command='cat ~/.hello').body.strip()
# print(response)
# assert response == 'hello'


# crds = client.custom_resource_definitions.get().all()



# from kubed.tools.leader import LeaderElection
#
# identity = 'couchdb-1'
# election = LeaderElection(
#     client, name='couchdb', namespace='default', identity=identity)
#
# with election:
#     election.start()
#     election.join()

# pods = client.pods.get().all()

# ep = client.endpoints.get(name='couchdb', namespace='default').first()
# ep.annotate(some='something2', resource_version=1)

# from kubed.tools.resource_lock import EndpointsLock
# lock = EndpointsLock(client, identity, 'couchdb', 'default')
# rec = lock.get()
