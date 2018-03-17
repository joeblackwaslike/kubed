from .. import strutil


class Singleton(type):
    """Metaclass for singletons. Any instantiation of a Singleton class yields
    the exact same object, e.g.:

    >>> class MyClass(metaclass=Singleton):
            pass
    >>> a = MyClass()
    >>> b = MyClass()
    >>> a is b
    True
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

    @classmethod
    def __instancecheck__(mcs, instance):
        if instance.__class__ is mcs:
            return True
        else:
            return isinstance(instance.__class__, mcs)


class WrappedAttrs:
    def __getattribute__(self, name):
        try:
            if all([name != '_wrapped', not name.startswith('__')]):
            # if not name.startswith('_'):
                return object.__getattribute__(self._wrapped, name)
        except AttributeError:
            pass
        return object.__getattribute__(self, name)

    def __hasattr__(self, name):
        if all([name is not '_wrapped', not name.startswith('__')]):
        # if not name.startswith('_'):
            return hasattr(self._wrapped, name)
        return object.__hasattr__(self, name)

    def __setattr__(self, name, value):
        if all([name is not '_wrapped', not name.startswith('__')]):
        # if not name.startswith('_'):
            return setattr(self._wrapped, name, value)
        return object.__setattr__(self, name, value)


class WrappedMap:
    """Add dictionary accessor methods that wrap self._wrapped reference."""
    def __contains__(self, key):
        return key in self._wrapped

    def __getitem__(self, key):
        return self._wrapped[key]

    def __setitem__(self, key, value):
        self._wrapped[key] = value

    def __delitem__(self, key):
        del self._wrapped[key]

    def keys(self):
        """Return the wrapped object's keys method."""
        return self._wrapped.keys()

    def values(self):
        """Return the wrapped object's values method."""
        return self._wrapped.values()

    def items(self):
        """Return the wrapped object's items method."""
        return self._wrapped.items()

    def __iter__(self):
        return iter(self._wrapped)


class Proxy(WrappedAttrs, WrappedMap):
    # Required to implement
    _wrapped = None

    def __init__(self, *args, **kwargs):
        self.__dict__['_wrapped'] = args[0]

    def __isinstance__(self, *args, **kwargs):
        return self._wrapped.__isinstance__(self, *args, **kwargs)


class AttrDict(dict):
    """
    A class to convert a nested Dictionary into an object with key-values
    that are accessible using attribute notation (AttrDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttrDict.attr.attr)
    """

    def __init__(self, iterable, **kwargs):
        super(AttrDict, self).__init__(iterable, **kwargs)
        for key, value in iterable.items():
            if isinstance(value, dict):
                self.__dict__[key] = AttrDict(value)
            else:
                self.__dict__[key] = value
