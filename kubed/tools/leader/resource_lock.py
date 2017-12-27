from .constants import DEFAULT_TTL
from .record import LeaderElectionRecord
from ...exceptions import ResourceVersionConflictError


_RECORD_ANNOTATION_KEY = 'kubed.joeblack.nyc/leader'


class ResourceLock:
    def __init__(self, client, identity, name, namespace):
        self._client = client
        self.identity = identity
        self.name = name
        self.namespace = namespace

    def get(self):
        """Returns the current leader election annotation, and convert to
        record. if unsuccessful tries to create one for itself.
        """
        resource = self.get_resource()
        try:
            annotation = resource.metadata.annotations[_RECORD_ANNOTATION_KEY]
            record = LeaderElectionRecord.from_json(annotation)
            return record
        except (TypeError, KeyError):
            # the annotation doesn't exist or there are no annotations
            try:
                return self.create()
            except ResourceVersionConflictError:
                # get the leader record now that it's primed
                return self.get()

    def create(self):
        """Create attempts to create a LeaderElectionRecord for itself, using
        self.identity.
        """
        resource = self.get_resource()
        record = LeaderElectionRecord(self.identity)
        annotation = {_RECORD_ANNOTATION_KEY: record.to_json()}
        resource.annotate(resource.metadata.resource_version, **annotation)
        return record

    def __repr__(self):
        class_name = type(self).__name__
        return f'{class_name}({self.identity}/{self.name}/{self.namespace})'


class EndpointsLock(ResourceLock):
    def get_resource(self):
        return self._client.endpoints.get(
            name=self.name, namespace=self.namespace).first()
