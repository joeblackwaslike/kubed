import sys

import kubernetes
from kubernetes.client import ApisApi, CustomObjectsApi

from kubed import util
from ..meta.decorators import cached
from ..objects.api.groups import CustomAPIGroupBase


_NATIVE_API_GROUPS = (
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


class _ObjectAPIsGroupBase:
    def __init__(self, name):
        self.name = name

    @property
    def native(self):
        return True

    def to_class(self, versioned=False):
        # if self.native:
        name = self.name.split('.k8s.io')[0].capitalize()
        name = ''.join([p.capitalize() for p in name.split('.')])
        if versioned:
            version = self.version
            if version.startswith('v1'):
                name += version.replace('v', 'V', 1)
        import_path = f'kubernetes.client.apis.{name}Api'
        return util.import_path(import_path)

    def to_obj(self, client=None, versioned=False):
        return self.to_class(versioned)(client)

    @property
    def version(self):
        return self.to_obj().get_api_group().preferred_version.version

    @property
    def versioned(self):
        return self.to_obj().get_api_group().preferred_version.group_version

    def __repr__(self):
        class_name = type(self)
        return f'{class_name}({self.name})'


class _NativeObjectAPIsGroup(_ObjectAPIsGroupBase):
    pass


class _CustomObjectAPIsGroup(_ObjectAPIsGroupBase):
    @property
    def native(self):
        return False

    def to_class(self):
        return CustomObjectAPI.api_for(self.name)

    def to_obj(self, client=None):
        return self.to_class()(client)


class CustomObjectAPI:
    def __init__(self, client=None):
        self._client = client
        self._api = CustomObjectsApi(self._client)

    @classmethod
    def api_for(cls, group):
        subclasses = cls.__subclasses__()
        return [c for c in subclasses if c._api_group == group][0]

    def get_api_group(self):
        groups = ApisApi().get_api_versions().groups
        return [group for group in groups if group.name == self._api_group][0]

    @property
    def version(self):
        return self.get_api_group().preferred_version.version

    # @classmethod
    # def custom_objects(cls):
    #     subclasses = cls.__subclasses__()
    #     return {subclass._plural_name: subclass
    #             for subclass in subclasses}.items()


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
        elif key in _NATIVE_API_GROUPS:
            return _NativeObjectAPIsGroup(key)
        else:
            return _CustomObjectAPIsGroup(key)

    def __getitem__(self, key):
        class_ = self._getclass(key)
        if isinstance(class_, _CustomObjectAPIsGroup):
            return class_.to_obj(self.client)
        elif isinstance(class_, _NativeObjectAPIsGroup):
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
