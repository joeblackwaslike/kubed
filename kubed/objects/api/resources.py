"""

[todo] replace checks for _namespaced with issubclass(obj, Namespaced)
"""
from datetime import timedelta

from . import util
from .bases import APIObjectBase
from .groups import (
    CoreAPIGroup,
    ExtensionsAPIGroup,
    AppsAPIGroup,
    BatchAPIGroup,
    APIextensionsAPIGroup
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


class Pod(Namespaced, Phased, APIObjectBase, CoreAPIGroup):
    def exec(self, command=None, container=None, shell=None, interactive=False,
            tty=False, **kwargs):
        container = container or self.spec.containers[0].name
        # [fixme] even though stdout by default is True, this is required to
        #         make exec work properly.
        # INFO: this kwarg itself isn't required, but one of stdout,
        #       stderr, or stdin set to True is.  Investigate later
        # edit: this if fixed here:
        #   https://github.com/kubernetes-client/python-base/pull/35/files
        # but not in the latest version of the python client yet
        if all([not kwargs.get('stdout'),
                not kwargs.get('stderr'),
                not kwargs.get('stdin')]):
            kwargs['stdout'] = True
        if interactive:
            kwargs['stdin'] = True
            kwargs['_preload_content'] = False
        if tty:
            kwargs['tty'] = True

        request = rest.StreamRequest(
            self._manager.clone(),
            'exec',
            name=self.name,
            namespace=self.namespace,
            command=util.shlex(command, shell),
            container=container,
            **kwargs
        )
        return request.execute()

    def logs(self, container=None, follow=False, since=None, tail=None,
             previous=False, **kwargs):
        """Returns logs from the attached pod.

        args:
          since: timedelta, defaults to None.

        example:
          from datetime import timedelta
          logs = pod.logs(since=timedelta(minutes=5))

        [todo] implement streaming logs with follow=True
        """
        container = container or self.spec.containers[0].name
        if follow:
            kwargs['_preload_content'] = False
        if since:
            if isinstance(since, timedelta):
                since = round(since.total_seconds())
            kwargs['since_seconds'] = since
        if tail:
            kwargs['tail_lines'] = tail

        request = rest.Request(
            self._manager.clone(),
            'logs',
            name=self.name,
            namespace=self.namespace,
            container=container,
            previous=previous,
            follow=follow,
            **kwargs
        )
        return request.execute()


class Node(APIObjectBase, CoreAPIGroup):
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


class ConfigMap(Namespaced, Configuration, APIObjectBase, CoreAPIGroup):
    pass


class Secret(Namespaced, Configuration, Encoded, APIObjectBase, CoreAPIGroup):
    _transforms = APIObjectBase._transforms + ('B64TranslateMap',)


class Endpoints(Namespaced, APIObjectBase, CoreAPIGroup):
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


class Service(Namespaced, Selecting, APIObjectBase, CoreAPIGroup):
    @property
    def type(self):
        return self.spec.type


class ReplicaSet(Namespaced, Replicating, Selecting, APIObjectBase,
                 ExtensionsAPIGroup):
    pass


class Deployment(Namespaced, Replicating, Selecting, APIObjectBase,
                 ExtensionsAPIGroup):
    pass


class StatefulSet(Namespaced, Replicating, Selecting, APIObjectBase,
                  AppsAPIGroup):
    pass


class DaemonSet(Namespaced, Replicating, Selecting, APIObjectBase,
                ExtensionsAPIGroup):
    @property
    def ready(self):
        return all([
            self.status.observed_generation >= self.metadata.generation,
            self.status.desired_number_scheduled == self.status.number_ready]
        )


class Ingress(Namespaced, APIObjectBase, ExtensionsAPIGroup):
    pass


class Namespace(APIObjectBase, CoreAPIGroup):
    pass


class Job(Namespaced, Selecting, APIObjectBase, BatchAPIGroup):
    @property
    def complete(self):
        for condition in self.status.conditions:
            if condition.type == 'Complete' and condition.status == 'True':
                return True
        return False

    @property
    def succeeded(self):
        return self.status.succeeded >= len(self.spec.template.spec.containers)


class CronJob(Namespaced, Selecting, APIObjectBase, BatchAPIGroup):
    pass


class PersistentVolume(Storage, Bindable, APIObjectBase, CoreAPIGroup):
    @property
    def claim(self):
        ref = self.spec.claim_ref
        manager = self._manager.client.manager_for(ref.kind)
        return manager.get(
            name=ref.name, namespace=ref.namespace).first()


class PersistentVolumeClaim(Namespaced, Storage, Bindable, APIObjectBase,
                            CoreAPIGroup):
    @property
    def volume(self):
        manager = self._manager.client.manager_for('PersistentVolume')
        return manager.get(name=self.spec.volume_name).first()


class ServiceAccount(Namespaced, APIObjectBase, CoreAPIGroup):
    pass


class CustomResourceDefinition(APIObjectBase, APIextensionsAPIGroup):
    pass
