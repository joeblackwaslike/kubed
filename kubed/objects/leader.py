import time
from datetime import datetime, timedelta
import socket
import json
import threading


# _RECORD_ANNOTATION_KEY = 'leader-election.joeblack.nyc/leader'
# _DEFAULT_LEASE_TTL = 30
#
# #
# class ResourceLock:
#     def __init__(self, client, identity, name, namespace):
#         self._client = client
#         self.identity = identity
#         self.name = name
#         self.namespace = namespace
#
#     # returns the current leader election record
#     def get(self):
#         self._wrapped.reload()
#         annotation = self._wrapped.metadata.annotations[_RECORD_ANNOTATION_KEY]
#         return LeaderElectionRecord.from_json(annotation)
#
#     # Create attempts to create a LeaderElectionRecord
#     def create(self, record):
#         annotation = {_RECORD_ANNOTATION_KEY: record.to_json()}
#         self._wrapped.reload()
#         return self._wrapped.annotate(**annotation)
#
#     # Update will update an existing LeaderElectionRecord
#     def update(self, record):
#         return self.create(record)
#
#     def delete(self):
#         self._wrapped.reload()
#         if _RECORD_ANNOTATION_KEY in self._wrapped.metadata.annotations:
#             annotation = {_RECORD_ANNOTATION_KEY: None}
#             self._wrapped.annotate(**annotation)
#
#     @property
#     def __repr__(self):
#         return f'{self.identity}/{self.name}/{self.namespace}'

#
# class EndpointsLock(ResourceLock):
#     resource = 'endpoints'
#     def __init__(self, client, identity, name, namespace):
#         ResourceLock.__init__(self, client, identity, name, namespace)
#         self._wrapped = self._client.endpoints.get(
#             name=self.name, namespace=self.namespace).first()


# class LeaderElectionRecord:
#     def __init__(self, identity, duration=None, renew_time=None, acquire_time=None,
#                  transitions=0):
#         now = datetime.now()
#         # identity should be like endpointsName/namespace
#         self.identity = identity
#         duration = duration or _DEFAULT_LEASE_TTL
#         self.duration = timedelta(seconds=duration)
#         self.renew_time = renew_time or now + self.duration
#         self.acquire_time = acquire_time or now
#         self.transitions = transitions
#
#     @classmethod
#     def from_json(cls, blob):
#         data = json.loads(blob)
#         return cls(
#             identity=data['identity'],
#             duration=data['duration'],
#             renew_time=datetime.fromtimestamp(data['renew_time']),
#             acquire_time=datetime.fromtimestamp(data['acquire_time']),
#             transitions=data['transitions']
#         )
#
#     def to_json(self):
#         return json.dumps(dict(
#             identity=self.identity,
#             duration=self.duration.seconds,
#             renew_time=self.renew_time.timestamp(),
#             acquire_time=self.acquire_time.timestamp(),
#             transitions=self.transitions
#         ))
#
#
# class _CurrentRecord:
#     def __init__(self, record=None, time=None):
#         self.record = LeaderElectionRecord(None)
#         self.time = time or datetime.now()



# class LeaderElector(threading.Thread):
#     def __init__(self, client, name, namespace, identity=None,
#                  ttl=_DEFAULT_LEASE_TTL, debug=False):
#         threading.Thread.__init__(self)
#         self._client = client
#         self.name = name
#         self.namespace = namespace or self._client.namespace
#         self.ttl = timedelta(seconds=ttl)
#         self.debug = debug
#
#         self.identity = identity or socket.gethostname()
#         # self.current_record = None
#         # self.current_time = datetime.now()
#         self.current = _CurrentRecord()
#         self.lock = EndpointsLock(self._client, self.identity, name, namespace)
#         self.endpoints = self._client.endpoints.get(
#             name=name, namespace=namespace).first()
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, *args):
#         self._stop()
#
#     @property
#     def leading(self):
#         return self.leader.name == self.lock.identity
#
#     @property
#     def leader(self):
#         return self._client.pods.get(
#             name=self.current.record.identity,
#             namespace=self.namespace).first()
#
#     def _try_acquire_or_renew(self):
#         self.endpoints.reload()
#         now = datetime.now()
#         record = LeaderElectionRecord(
#             self.identity, duration=self.ttl.seconds, renew_time=now)
#         try:
#             old_record = self.lock.get()
#         except KeyError:
#             self.lock.create(record)
#             self.current.record = record
#             self.current.time = datetime.now()
#             return True
#
#         if record.__dict__ == old_record.__dict__:
#             self.current.record = old_record
#             self.current.time = datetime.now()
#
#         if ((self.current.time + self.ttl) > now and
#              old_record.identity != self.lock.identity):
#                 return False
#
#         if old_record.identity == self.lock.identity:
#             record.acquire_time = old_record.acquire_time
#             record.transitions = old_record.transitions
#         else:
#             record.transitions = old_record.transitions + 1
#
#         self.lock.update(record)
#         self.current.record = record
#         self.current.time = datetime.now()
#         return True
#
#     def _acquire(self):
#         while self._running:
#             succeeded = self._try_acquire_or_renew()
#             if not succeeded:
#                 if self.debug:
#                     print('current leaseholder is: {}'.format(self.leader))
#                 time.sleep(5)
#                 continue
#             return True
#
#     def _renew(self):
#         while self._running:
#             succeeded = self._try_acquire_or_renew()
#             if succeeded:
#                 if self.debug:
#                     expires = datetime.now() - self.current.record.renew_time
#                     print('current leaseholder is: {}'.format(self.leader))
#                     print('lease expires in {}'.format(expires.seconds))
#                 time.sleep(5)
#                 continue
#             return True
#
#     def run(self):
#         self._running = True
#         while self._running:
#             self._acquire()
#             self._renew()
#
#     def _stop(self):
#         self.lock.delete()
#         self._running = False
#
#     @property
#     def running(self):
#         return self._running
#
#     def __repr__(self):
#         class_name = type(self).__name__
#         alive = self.is_alive()
#         return f'{class_name}(running: {self.running}, alive: {alive})'
