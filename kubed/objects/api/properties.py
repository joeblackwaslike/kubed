import time


class Namespaced:
    _namespaced = True
    @property
    def namespace(self):
        return self.metadata.namespace


class Phased:
    @property
    def phase(self):
        return self.status.phase

    @property
    def ready(self):
        # [todo] check if there is a way this is already expressed through the
        # kubernetes api.
        statuses = [self.status.phase == 'Running']
        if self.status.container_statuses:
            statuses.extend(
                [status.ready for status in self.status.container_statuses])
        return all(statuses)

    def wait(self):
        while not self.ready:
            time.sleep(6)
            self.reload()
        self.reload()


class Configuration:
    def get(self, key, default=None):
        return self.data.get(key, default)

    def __repr__(self):
        class_name = type(self).__name__
        return f'{class_name}({self.name}/{self.namespace}: {self.data})'


class Encoded:
    pass


class Storage:
    pass


class Bindable:
    @property
    def phase(self):
        return self.status.phase

    @property
    def bound(self):
        return self.status.phase == 'Bound'


class Selecting:
    @property
    def pods(self):
        selectors = dict(label=self.spec.selector.match_labels)
        client = self._manager.client
        response = client.pods.get(self.namespace, selectors=selectors)
        return response.body


class Replicating:
    @property
    def ready(self):
        return all([
            self.status.observed_generation >= self.metadata.generation,
            self.status.replicas == self.status.ready_replicas]
        )

    def wait(self):
        while not self.ready:
            time.sleep(6)
            self.reload()
        self.reload()
