import kubernetes

from .config import load_config


class ClientContext:
    # set namespace here if you want to override the current namespace
    def __init__(self, config=None, client=None, namespace=None,
                 kube_context=None, **kwargs):
        self.config = config or load_config(namespace=namespace, **kwargs)
        if kube_context:
            self.client = client or kubernetes.config.new_client_from_config(
                context=kube_context)
        else:
            self.client = client or kubernetes.client.ApiClient(self.config)

    def __repr__(self):
        class_name = type(self).__name__
        if self.config.active_context:
            details += self.config.active_context['context']['cluster'] + ': '
        details += self.host
        if self.namespace:
            details += '/' + self.namespace
        return f'{class_name}({details})'
