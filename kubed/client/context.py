import kubernetes

from .config import load_config


class ClientContext:
    # set namespace here if you want to override the current namespace
    def __init__(self, config=None, client=None, namespace=None,
                 kube_context=None, **kwargs):
        self.config = config or load_config(namespace=namespace, **kwargs)
        # log_level = get_config('log_level', None, kwargs)
        # if log_level:
        #     console_handler = logging.StreamHandler()
        #     console_handler.setLevel(log_level.upper())
        #     self.config.logger_stream_handler = console_handler
        # self.config.proxy = get_config('proxy', None, kwargs)
        # self.config.debug = get_config('debug', None, kwargs)
        # self.config.domain = get_config('kube_domain', 'cluster.local', kwargs)
        # self.namespace = namespace or self.config.namespace
        # self.extras = kwargs

        if kube_context:
            self.client = client or kubernetes.config.new_client_from_config(
                context=kube_context)
        else:
            self.client = client or kubernetes.client.ApiClient(self.config)


    def __repr__(self):
        class_name = type(self).__name__
        if self.cluster_context:
            details += self.cluster_context + ': '
        details += self.host
        if self.namespace:
            details += '/' + self.namespace
        return f'{class_name}({details})'
