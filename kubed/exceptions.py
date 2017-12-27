class KubedError(Exception):
    pass


class KubedConfigError(KubedError):
    pass


class KubedConfigNotFoundError(KubedConfigError):
    pass


class KubedConfigInvalidError(KubedConfigError):
    pass


class KubedApiError(KubedError):
    def __init__(self, message=None, response=None):
        self.message = message
        self.response = response

    def __str__(self):
        return f'{self.message} {self.response}'


class NoPodsFoundError(KubedApiError):
    pass


class ResourceVersionConflictError(KubedApiError):
    pass
