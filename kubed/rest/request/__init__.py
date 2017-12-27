from . import selectors, openapi, base


def request(*args, **kwargs):
    return base.Request(*args, **kwargs)
