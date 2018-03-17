import kubernetes
from kubernetes.client.rest import ApiException

from .properties import Namespaced
from ... import rest, strutil
from ...meta import pattern
from ...exceptions import ResourceVersionConflictError


class APIObjectBase(pattern.Proxy):
    _namespaced = False
    _transforms = ('ResourceWrapper', 'MissingFieldCopier')
    def __init__(self, manager, obj):
        pattern.Proxy.__init__(self, obj)
        self._manager = manager

    @classmethod
    def resource_for(cls, kind):
        subclasses = cls.__subclasses__()
        try:
            resource = [r for r in subclasses if r.__name__ == kind][0]
        except IndexError:
            kind = strutil.camel_case(kind)
            resource = [r for r in subclasses if r.__name__ == kind][0]
        return resource

    @property
    def name(self):
        return self.metadata.name

    def reload(self):
        new = self._manager.get(
            name=self.name, namespace=self.namespace).first()
        # [fixme] there has to be a better way to do this? but it works!
        self.__dict__.update(new.__dict__)

    # operates like: kubectl patch
    def patch(self, data, **kwargs):
        if kwargs.get('resource_version'):
            resource_version = kwargs.pop('resource_version')
            # important to use resourceVersion not resource_version here
            data['metadata']['resourceVersion'] = str(resource_version)
        request = rest.Request(
            self._manager.clone(),
            'patch',
            name=self.name,
            namespace=getattr(self, 'namespace', None),
            body=data
        )
        try:
            new = request.execute().first()
        except ApiException as err:
            if 'object has been modified' in err.body:
                raise ResourceVersionConflictError from err
            raise

        # [fixme] see above
        self.__dict__.update(new.__dict__)
        return new

    # set a label's value to None to remove it
    def label(self, resource_version=None, **labels):
        data = dict(
            metadata=dict(
                labels=labels
            )
        )
        return self.patch(data, resource_version=resource_version)

    # set an annotation's value to None to remove it
    def annotate(self, resource_version=None, **annotations):
        data = dict(
            metadata=dict(
                annotations=annotations
            )
        )
        return self.patch(data, resource_version=resource_version)

    # operates like: kubectl rolling-update, kubectl apply and kubectl replace
    def replace(self):
        request = rest.Request(
            self._manager.clone(),
            'replace',
            name=self.name,
            namespace=self.namespace,
            body=self._wrapped
        )
        new = request.execute().first()
        # [fixme] also see above
        self.__dict__.update(new.__dict__)
        return new

    # operates like: kubectl delete
    def delete(self, **options):
        request = rest.Request(
            self._manager.clone(),
            'delete',
            name=self.name,
            namespace=self.namespace,
            body=kubernetes.client.V1DeleteOptions(**options)
        )
        return request.execute()

    def __repr__(self):
        class_name = type(self).__name__
        details = self.name
        if self._namespaced:
            details += '/' + self.namespace
        return f'{class_name}({details})'


class CustomObjectBase(APIObjectBase):
    _transforms = ('CustomObjectWrapper',)
    def __init__(self, manager, obj):
        APIObjectBase.__init__(self, manager, obj)

    @classmethod
    def custom_objects(cls):
        subclasses = cls.__subclasses__()
        return {subclass._plural_name: subclass
                for subclass in subclasses}.items()
