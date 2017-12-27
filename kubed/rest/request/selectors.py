SELECTOR_TEMPLATES = dict(
    label='{kind}_selector'
)


class RequestSelector:
    """Contains information and logic for filtering API requests.
    """

    def __init__(self, kind, selector):
        self.kind = kind
        self.selector = selector

    def parameterize(self):
        return self._parameterize(self.selector)

    def _render(self, template):
        return SELECTOR_TEMPLATES[template].format(**self.__dict__)

    @property
    def label(self):
        return self._render('label')

    @staticmethod
    def _parameterize(selector):
        if isinstance(selector, str):
            return selector
        params = []
        for key, val in selector.items():
            parts = key.split('__')
            if len(parts) == 1:
                label, op = parts[0], 'eq'
            else:
                label, op = parts[0], parts[1]
            if op == 'eq':
                params.append('{}={}'.format(label, val))
            elif op == 'neq':
                params.append('{} != {}'.format(label, val))
            elif op == 'in':
                params.append('{} in ({})'.format(label, ','.join(val)))
            elif op == 'notin':
                params.append('{} notin ({})'.format(label, ','.join(val)))
            else:
                raise ValueError('Invalid operator: {}'.format(op))
        return ','.join(params)
