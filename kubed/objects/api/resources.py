"""

[todo] replace checks for _namespaced with issubclass(obj, Namespaced)
"""

from . import util
from .bases import APIObjectBase
from .groups import (
    CoreApiGroup,
    ExtensionsApiGroup,
    AppsApiGroup,
    BatchApiGroup,
    ApiextensionsApiGroup
)
from .properties import (
    Namespaced,
    Phased,
    Configuration,
    Encoded,
    Replicating,
    Selecting,
    Storage,
    Bindable
)
from ... import rest


class Pod(Namespaced, Phased, APIObjectBase, CoreApiGroup):
    def exec(self, command=None, container=None, shell=None, interactive=False,
            tty=False, **kwargs):

        kwargs['stream'] = True
        # [fixme] even though stdout by default is True, this is required to
        #         make exec work properly.
        # INFO: this kwarg itself isn't required, but one of stdout,
        #       stderr, or stdin set to True is.  Investigate later
        if all([not kwargs.get('stdout'),
                not kwargs.get('stderr'),
                not kwargs.get('stdin')]):
            kwargs['stdout'] = True
        if interactive:
            kwargs['stdin'] = True
            kwargs['_preload_content'] = False
        if tty:
            kwargs['tty'] = True

        request = rest.request(
            self._manager.clone(),
            'exec',
            name=self.name,
            namespace=self.namespace,
            command=util.shlex(command, shell),
            **kwargs
        )
        return request.execute()

    # [todo] make follow=True work with streaming
    def logs(self, container=None, follow=None, since=None, tail=None,
             previous=False, **kwargs):
        """Returns logs from the attached pod.

        args:
          since: timedelta, defaults to None.

        example:
          from datetime import timedelta
          logs = pod.logs(since=timedelta(minutes=5))

        [todo] implement streaming logs with follow=True
        """
        # if follow:
        #     kwargs['stream'] = True
        #     kwargs['_preload_content'] = False
        #     kwargs['follow'] = True
        if since:
            kwargs['since_seconds'] = round(since.total_seconds())
        if tail:
            kwargs['tail_lines'] = tail

        request = rest.request(
            self._manager.clone(),
            'logs',
            name=self.name,
            namespace=self.namespace,
            container=container,
            previous=previous,
            **kwargs
        )
        return request.execute()


class Node(APIObjectBase, CoreApiGroup):
    @property
    def ready(self):
        for condition in self.status.conditions:
            if condition.type == 'Ready' and condition.status == 'True':
                return True
        return False

    @property
    def address(self):
        for addr in self.status.addresses:
            if addr.type == 'InternalIP':
                return addr.address

    @property
    def hostname(self):
        for addr in self.status.addresses:
            if addr.type == 'Hostname':
                return addr.address

    def wait(self):
        while not self.ready:
            time.sleep(6)
            self.reload()
        self.reload()


class ConfigMap(Namespaced, Configuration, APIObjectBase, CoreApiGroup):
    pass


class Secret(Namespaced, Configuration, Encoded, APIObjectBase, CoreApiGroup):
    _transforms = ('B64TranslateMap',)


class Endpoints(Namespaced, APIObjectBase, CoreApiGroup):
    @property
    def _addresses(self):
        return [address for address in self.subsets[0].addresses]

    @property
    def nodes(self):
        return [address.node_name for address in self._addresses]

    @property
    def ips(self):
        return [address.ip for address in self._addresses]

    @property
    def _targets(self):
        references = [address.target_ref for address in self._addresses]
        return [(ref.kind, ref.name, ref.namespace) for ref in references]

    @property
    def pods(self):
        objects = []
        for kind, name, namespace in self._targets:
            manager = self._manager.client.manager_for(kind)
            objects.append(manager.get(name=name, namespace=namespace).first())
        return objects
        # return [pods_manager.get(name=name, namespace=namespace).first()
        #         for name, namespace in self._targets]


class Service(Namespaced, Selecting, APIObjectBase, CoreApiGroup):
    @property
    def type(self):
        return self.spec.type


class ReplicaSet(Namespaced, Replicating, Selecting, APIObjectBase,
                 ExtensionsApiGroup):
    pass


class Deployment(Namespaced, Replicating, Selecting, APIObjectBase,
                 ExtensionsApiGroup):
    pass


class StatefulSet(Namespaced, Replicating, Selecting, APIObjectBase,
                  AppsApiGroup):
    pass


class DaemonSet(Namespaced, Replicating, Selecting, APIObjectBase,
                ExtensionsApiGroup):
    @property
    def ready(self):
        return all([
            self.status.observed_generation >= self.metadata.generation,
            self.status.desired_number_scheduled == self.status.number_ready]
        )


class Ingress(Namespaced, APIObjectBase, ExtensionsApiGroup):
    pass


class Namespace(APIObjectBase, CoreApiGroup):
    pass


class Job(Namespaced, Selecting, APIObjectBase, BatchApiGroup):
    @property
    def complete(self):
        for condition in self.status.conditions:
            if condition.type == 'Complete' and condition.status == 'True':
                return True
        return False

    @property
    def succeeded(self):
        return self.status.succeeded >= len(self.spec.template.spec.containers)


class PersistentVolume(Storage, Bindable, APIObjectBase, CoreApiGroup):
    @property
    def claim(self):
        ref = self.spec.claim_ref
        manager = self._manager.client.manager_for(ref.kind)
        return manager.get(
            name=ref.name, namespace=ref.namespace).first()


class PersistentVolumeClaim(Namespaced, Storage, Bindable, APIObjectBase,
                            CoreApiGroup):
    @property
    def volume(self):
        manager = self._manager.client.manager_for('PersistentVolume')
        return manager.get(name=self.spec.volume_name).first()


class ServiceAccount(Namespaced, APIObjectBase, CoreApiGroup):
    pass


class CustomResourceDefinition(APIObjectBase, ApiextensionsApiGroup):
    pass
