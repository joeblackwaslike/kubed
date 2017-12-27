import os
import logging
from os.path import join, dirname, expanduser

import yaml

import kubernetes
from kubernetes.client import Configuration
from kubernetes.config import kube_config, incluster_config

from ..meta import pattern
from ..exceptions import KubedConfigNotFoundError, KubedConfigInvalidError


def incluster():
    # If we're in a kubernetes cluster as a pod, we'll have the following
    # environment variable populated.
    return os.getenv('KUBERNETES_SERVICE_PORT')


def load_config(*args, **kwargs):
    if incluster():
        return _InClusterConfig(*args, **kwargs)
    return _KubeConfig(*args, **kwargs)


def _load_kube_config(*args, **kwargs):
    try:
        kube_config.load_kube_config()
    except kubernetes.ConfigException as exc:
        if 'File does not exist' in exc.message:
            raise KubedConfigNotFound from exc
        elif 'Invalid kube-config file' in exc.message:
            raise KubedConfigInvalid from exc

    config = Configuration()

    config_path = kwargs.get(
        'config_file',
        expanduser(kube_config.KUBE_CONFIG_DEFAULT_LOCATION)
    )
    with open(config_path) as fd:
        data = yaml.load(fd)

    current_ctx = data['current-context']
    for context in data['contexts']:
        if context['name'] == current_ctx:
            config.namespace = context['context']['namespace']
    config.dns_domain = os.getenv('KUBE_DOMAIN', 'cluster.local')
    Configuration.set_default(config)
    return Configuration._default


def _load_incluster_config():
    incluster_config.load_incluster_config()
    config = Configuration()

    namespace_path = join(
        dirname(incluster_config.SERVICE_CERT_FILENAME), 'namespace'
    )
    with open(namespace_path) as fd:
        config.namespace = fd.read().strip()

    # [todo] is there a better way to do this?
    with open('/etc/resolv.conf') as fd:
        data = fd.read().strip().split('\n')
        config.dns_domain = [line for line in data
                             if line.startswith('search')][0].split()[3]

    Configuration.set_default(config)
    return Configuration._default


def get_config(key, default=None, kwargs=None):
    kwargs = kwargs or {}
    output = os.getenv('KUBE' + key.upper(), kwargs.pop(key, default))
    if output is 'false':
        return False
    elif output is 'true':
        return True
    else:
        return output


class _ConfigBase(pattern.Proxy):
    def __init__(self, *args, **kwargs):
        config = self._config_loader()
        pattern.Proxy.__init__(self, config, *args, **kwargs)

        self.assert_hostname = False
        log_level = get_config('log_level', None, kwargs)
        if log_level:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level.upper())
            self.logger_stream_handler = console_handler

        self.proxy = get_config('proxy', None, kwargs)
        self.debug = get_config('debug', None, kwargs)
        self.domain = get_config('domain', 'cluster.local', kwargs)
        self.namespace = kwargs.pop('namespace', self.namespace)
        self._extras = kwargs


class _InClusterConfig(_ConfigBase):
    _config_loader = _load_incluster_config
    def __init__(self, *args, **kwargs):
        _ConfigBase.__init__(self, *args, **kwargs)



class _KubeConfig(_ConfigBase):
    _config_loader = _load_kube_config
    def __init__(self, *args, **kwargs):
        _ConfigBase.__init__(self, *args, **kwargs)

    @property
    def contexts(self):
        contexts, _ = kube_config.list_kube_config_contexts()
        return contexts

    @property
    def active_context(self):
        _, active_context = kube_config.list_kube_config_contexts()
        return active_context

    def __repr__(self):
        class_name = type(self).__name__
        return f'{class_name} {self.active_context}'
