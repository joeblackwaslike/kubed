from datetime import datetime, timedelta
import json

from .constants import DEFAULT_TTL


class LeaderElectionRecord:
    def __init__(self, identity, expires=None):
        self.identity = identity
        self.expires = expires or self._get_expire_time()

    @staticmethod
    def _get_expire_time(renew=False):
        seconds = DEFAULT_TTL
        if renew:
            seconds = round(seconds/2)
        return datetime.now() + timedelta(seconds=seconds)

    @property
    def expired(self):
        return datetime.now() >= self.expires

    @property
    def should_renew(self):
        return self._get_expire_time(renew=True) >= self.expires

    def to_json(self):
        return json.dumps(dict(
            identity=self.identity,
            expires=self.expires.timestamp()
        ))

    @classmethod
    def from_json(cls, data):
        data = json.loads(data)
        return cls(
            identity=data['identity'],
            expires=datetime.fromtimestamp(data['expires'])
        )

    def __repr__(self):
        class_name = type(self).__name__
        rep = self.to_json()
        return f'{class_name}({rep})'
