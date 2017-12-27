# from os.path import dirname, join, abspath
# import sys
#
# this_dir = abspath(join(__file__, '..', '..'))
# sys.path.insert(0, this_dir)

import os
import logging

# import kubernetes
# from kubernetes.client.rest import ApiException

# import kubed
from kubed import ClientContext, APIClient
import time

DEBUG = False

if DEBUG:
    os.putenv('KUBE_DEBUG', 'true')
    logging.basicConfig(level=logging.DEBUG)

client = APIClient()


crds = client.custom_resource_definitions.get().all()

# from kubed.tools.leader import LeaderElection
#
# identity = 'couchdb-1'
# election = LeaderElection(
#     client, name='couchdb', namespace='default', identity=identity)
#
# with election:
#     election.start()
#     election.join()

# pods = client.pods.get().all()

# ep = client.endpoints.get(name='couchdb', namespace='default').first()
# ep.annotate(some='something2', resource_version=1)

# from kubed.tools.resource_lock import EndpointsLock
# lock = EndpointsLock(client, identity, 'couchdb', 'default')
# rec = lock.get()
