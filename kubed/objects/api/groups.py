class APIGroupBase:
    pass


class CoreAPIGroup(APIGroupBase):
    _api_group = 'core'


class ExtensionsAPIGroup(APIGroupBase):
    _api_group = 'extensions'


class AppsAPIGroup(APIGroupBase):
    _api_group = 'apps'


class BatchAPIGroup(APIGroupBase):
    _api_group = 'batch'


class APIextensionsAPIGroup(APIGroupBase):
    _api_group = 'apiextensions.k8s.io'


class CustomAPIGroupBase(APIGroupBase):
    pass
