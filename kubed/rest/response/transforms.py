from ... import objects, strutil
from ...meta import pattern


class TransformBase:
    def __init__(self, response):
        self.response = response

    @classmethod
    def transform_for(self, name):
        for subclass in self.__subclasses__():
            if subclass.__name__ == name:
                return subclass

    def apply(self):
        self.response.body = [self.operation(obj) for obj in self.response.body]

    def operation(self, obj):
        raise NotImplementedError(
            '{} must implement `operation` method', type(self).__name__)


class MissingFieldCopier(TransformBase):
    def operation(self, obj):
        if not obj.kind:
            obj.kind = self.response.resource.__name__
        if not obj.api_version:
            obj.api_version = self.response.raw.api_version
        return obj


class ResourceWrapper(TransformBase):
    def operation(self, obj):
        if not isinstance(obj, objects.APIObjectBase):
            return self.response.resource(self.response.manager, obj)


class B64TranslateMap(TransformBase):
    class _B64TranslatedMapWrapper(pattern.WrappedMap):
        def __init__(self, *args, **kwargs):
            self.__dict__['_wrapped'] = args[0]

        def __getitem__(self, key):
            return strutil.b64decode(self._wrapped[key])

        def __setitem__(self, key, value):
            self._wrapped[key] = strutil.b64encode(value)

        def get(self, key, default=None):
            return strutil.b64decode(self._wrapped.get(key, default))

        def values(self):
            for value in self._wrapped.items():
                yield strutil.b64decode(value)

        def items(self):
            for key, value in self._wrapped.items():
                yield key, strutil.b64decode(value)

        def __repr__(self):
            return f'{dict(self.items())}'

    def apply(self):
        for obj in self.response.body:
            obj.data = self.operation(obj.data)

    def operation(self, obj):
        return self._B64TranslatedMapWrapper(obj)
