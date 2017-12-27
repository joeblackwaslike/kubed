import sys


def import_path(name):
    module_segments = name.split('.')
    last_error = None
    remainder = []

    while module_segments:
        module_name = '.'.join(module_segments)
        try:
            __import__(module_name)
        except ImportError:
            last_error = sys.exc_info()[1]
            remainder.append(module_segments.pop())
            continue
        else:
            break
    else:
        raise ImportError('module could not be imported')
    module = sys.modules[module_name]
    nonexistent = object()
    for segment in reversed(remainder):
        module = getattr(module, segment, nonexistent)
        if module is nonexistent:
            raise ImportError('module could not be imported')
    return module


def import_safely(name, default=None):
    try:
        return import_path(name)
    except ImportError:
        return default
