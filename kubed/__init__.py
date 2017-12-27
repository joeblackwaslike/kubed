"""
kzconfig
~~~~~

Kazoo config library.

Kazoo configuration library for configuring kazoo within a kubernetes cluster.
This library includes a sup cli command for invoking sup against a remote
kazoo container.
"""

__title__ = 'kubed'
__version__ = '0.3.0'
__author__ = "Joe Black <me@joeblack.nyc>"
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 Joe Black'

from . import patch

patch.fix_api_group_null_value()

from . import strutil, exceptions, meta, client, objects, rest
from .client import ClientContext, APIClient
from .exceptions import (
    KubedError,
    KubedConfigError,
    KubedApiError,
    KubedConfigNotFoundError,
    KubedConfigInvalidError,
    NoPodsFoundError,
    ResourceVersionConflictError
)
