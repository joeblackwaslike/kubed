from . import selectors
from ..constants import NAMESPACE_DEFAULT, NAMESPACE_NONE
from ... import strutil


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


class _RequestParams:
    """Builds all keyword parameters for executing an API Request.
    """

    def __init__(self, request, manager, namespace, **kwargs):
        if request.resource._namespaced:
            if namespace is NAMESPACE_DEFAULT:
                namespace = manager.namespace
        else:
            namespace = None
        self.namespace = namespace

        self.name = kwargs.pop('name', None)
        self.selectors = kwargs.pop('selectors', None)
        if self.selectors:
            for label, sel in self.selectors.items():
                self.selectors[label] = selectors.RequestSelector(label, sel)

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
        if action == 'get' and request.by_name:
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
