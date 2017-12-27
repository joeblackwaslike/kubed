from . import selectors
from ..constants import NAMESPACE_DEFAULT, NAMESPACE_NONE
from ... import strutil


ARG_NAMES_WATCH = ('timeout_seconds', 'resource_version')
ARG_NAMES_STREAM = ('timeout')

API_ACTIONS_MAP = dict(
    get='list',
    get_by_name='read',
    create='create',
    patch='patch',
    replace='replace',
    delete='delete',
    exec='connect_get',
    logs='read'
)

NAMESPACE_TEMPLATES = dict(
    one='{action}_namespaced_{resource}',
    all='{action}_{resource}_for_all_namespaces',
    non='{action}_{resource}'
)


def method(*args, **kwargs):
    return _RequestMethod(*args, **kwargs)


def params(*args, **kwargs):
    return _RequestParams(*args, **kwargs)


class _RequestParams:
    """Builds all keyword parameters for executing an API Request.
    """

    def __init__(self, request, manager, namespace, **kwargs):
        namespace = namespace or None
        if request.resource._namespaced:
            if namespace is NAMESPACE_DEFAULT:
                namespace = manager.namespace
        self.namespace = namespace

        self.name = kwargs.pop('name', None)
        self.selectors = kwargs.pop('selectors', None)
        if self.selectors:
            for label, sel in self.selectors.items():
                self.selectors[label] = selectors.RequestSelector(label, sel)

        self._watched = kwargs.pop('watch', False)
        if self.watched:
            self.watch = {}
            for name in ARG_NAMES_WATCH:
                if name in kwargs:
                    self.watch[name] = kwargs.pop(name)

        self._streamed = kwargs.pop('stream', False)
        if self.streamed:
            self.stream = {}
            for name in ARG_NAMES_STREAM:
                if name in kwargs:
                    self.stream[name] = kwargs.poo(name)

        self.params = kwargs

    def build(self):
        params = self.params
        for param in ('name', 'namespace'):
            if getattr(self, param):
                params[param] = getattr(self, param)
        if self.selectors:
            for sel in self.selectors.values():
                params[sel.label] = sel.parameterize()
        return params

    @property
    def streamed(self):
        return bool(self._streamed)

    @property
    def watched(self):
        return bool(self._watched)

    @property
    def named(self):
        return bool(self.name)

    @property
    def namespaced(self):
        return all([
            bool(self.namespace),
            self.namespace is not NAMESPACE_NONE
        ])


class _RequestMethod:
    """Resolves the proper OpenAPI method to execute for an API Request.
    """

    def __init__(self, request, action, resource):
        self.request = request
        self.resource = resource
        if action == 'get' and request.named:
            action = 'get_by_name'
        self.action = action

    def _render(self, template):
        kwargs = dict(
            action=API_ACTIONS_MAP[self.action],
            resource=strutil.snake_case(self.resource.__name__)
        )
        output = NAMESPACE_TEMPLATES[template].format(**kwargs)
        # [todo] replace the following with something more pythonic
        #        maybe prefix/suffix maps?
        if self.action == 'exec':
            output += '_exec'
        elif self.action == 'logs':
            output += '_log'
        return output

    @property
    def name(self):
        if self.resource._namespaced:
            if self.request.namespaced:
                return self._render('one')
            else:
                return self._render('all')
        return self._render('non')

    @property
    def ref(self):
        api = self.request.manager.api
        return getattr(api, self.name)

    def __call__(self, *args, **kwargs):
        method = self.ref
        return method(*args, **kwargs)
