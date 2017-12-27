import sys

import kubernetes

from kubed import util
from ..meta.decorators import cached


_KUBERNETES_API_GROUPS = (
    'apiextensions.k8s.io',
    'apiregistration.k8s.io',
    'apps',
    'authentication.k8s.io',
    'authorization.k8s.io',
    'autoscaling',
    'batch',
    'certificates.k8s.io',
    'extensions',
    'networking.k8s.io',
    'policy',
    'rbac.authorization.k8s.io',
    # 'rook.io',
    'storage.k8s.io'
)


class _KubeAPIGroup:
    _custom_groups = {}
    def __init__(self, name):
        self.name = name

    @property
    def kubernetes_native(self):
        return self.name in _KUBERNETES_API_GROUPS

    def to_class(self, versioned=False):
        if self.kubernetes_native:
            name = self.name.split('.k8s.io')[0].capitalize()
            name = ''.join([p.capitalize() for p in name.split('.')])
            if versioned:
                version = self.version
                if version.startswith('v1'):
                    name += version.replace('v', 'V', 1)
            import_path = f'kubernetes.client.apis.{name}Api'
            return util.import_path(import_path)
        else:
            for key in self._custom_groups.keys():
                if self.name == key:
                    return self._custom_groups[key]
            else:
                raise NotImplemented(
                    'api group: %s is not implemented', self.name)

    def to_obj(self, client=None, versioned=False):
        return self.to_class(versioned)(client)

    @property
    def version(self):
        return self.to_obj().get_api_group().preferred_version.version

    @property
    def versioned(self):
        return self.to_obj().get_api_group().preferred_version.group_version

    @classmethod
    def register_custom(cls, group):
        if isinstance(group, str):
            group = util.import_path(group)
        name = group.__name__
        cls._custom_groups[name] = group

    def __repr__(self):
        class_name = type(self)
        return f'{class_name}({self.name})'


class _KubeAPIs:
    """Kubernetes API objects wrapper

    A facade class that attempts to wrap the numerous (and often irrelavent)
    Kubernetes API classes and return only the correct one after sacrificing
    a dozen goats to the k8s god.

    [todo] add multiple version support using preferred versions
    """

    def __init__(self, client):
        self.client = client

    @cached
    def _getclass(self, key):
        if key in ('', 'core'):
            return kubernetes.client.CoreV1Api
        return _KubeAPIGroup(key)

    def __getitem__(self, key):
        class_ = self._getclass(key)
        if isinstance(class_, _KubeAPIGroup):
            return class_.to_obj(self.client, versioned=True)
        return class_(self.client)

    def __contains__(self, key):
        try:
            return bool(self.__getitem__(key))
        except IndexError:
            return True

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except IndexError:
            return default
