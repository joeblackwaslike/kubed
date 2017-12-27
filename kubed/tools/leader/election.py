import time
import socket
import threading

from .constants import DEFAULT_SYNC_INTERVAL
from .record import LeaderElectionRecord
from .resource_lock import EndpointsLock
from ...exceptions import ResourceVersionConflictError
from ...client import APIClient


class LeaderElection(threading.Thread):
    """Elect the leader for a specified kubernetes endpoint object

    Example:
        from kubed.tools.leader import LeaderElection

        election = LeaderElection(client, name='couchdb', namespace='default')
        with election:
            election.start()
            # insert event loop here
    """

    def __init__(self, client=None, name='none', namespace=None, identity=None):
        threading.Thread.__init__(self)
        self._client = client or APIClient()
        self.name = name
        self.namespace = namespace or self._client.namespace
        self.identity = identity or socket.gethostname()
        self.lock = EndpointsLock(
            self._client, self.identity, self.name, self.namespace)
        self.running = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.running = False

    @property
    def leader(self):
        return self.lock.get()

    def _try_acquire_lease(self):
        """Try to acquire leader lease.

        Returns:
          True if successful, False otherwise.
        """
        record = self.lock.get()
        if record.identity is self.identity:
            return True
        if record.expired:
            try:
                record = self.lock.create()
                return True
            except ResourceVersionConflictError:
                return False
        return False

    def _try_renew_lease(self):
        """Try to renew existing lease.

        Returns:
          True if successful, False otherwise.
        """
        record = self.lock.get()
        if record.identity != self.identity:
            return False
        if record.should_renew:
            self.lock.create() # lock.create() can also renew lease
        return True

    def _acquire(self):
        """Continually try to acquire a lease while running and lease not
        already acquired.
        """
        while self.running and not self._try_acquire_lease():
            print('trying to acquire lease')
            print('leader: ', self.leader)
            time.sleep(DEFAULT_SYNC_INTERVAL)
        return True

    def _renew(self):
        """Continually renew acquired lease while running until not running or
        renew is not successful.
        """
        while self.running and self._try_renew_lease():
            print('renewing lease')
            print('leader: ', self.leader)
            time.sleep(DEFAULT_SYNC_INTERVAL)

    def run(self):
        self.running = True
        while self.running:
            self._acquire()
            self._renew()

    def stop(self):
        self.running = False

    def __repr__(self):
        class_name = type(self).__name__
        alive = self.is_alive()
        return f'{class_name}(running: {self.running}, alive: {alive})'
