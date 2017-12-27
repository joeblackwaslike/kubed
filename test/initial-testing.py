import os
from os.path import dirname, join, abspath
import sys

this_dir = abspath(join(__file__, '..', '..'))
sys.path.insert(0, this_dir)

import logging
from datetime import timedelta
import hashlib

import kubernetes
from kubernetes.client.rest import ApiException
kubernetes.client.Configuration

import kubed
from kubed import APIClient, ClientContext


DEBUG = False

if DEBUG:
    os.putenv('KUBE_DEBUG', 'true')
    logging.basicConfig(level=logging.DEBUG)

client = APIClient()


print('BEGIN TESTING')

print('testing client')
assert kubernetes.client.Configuration._default is not None
assert client.configuration.assert_hostname == False
assert isinstance(client.configuration, kubed.client.config._KubeConfig)
assert (
    client.configuration._wrapped.__dict__ ==
    kubernetes.client.Configuration._default.__dict__
)


print('testing pod create by composition')
pod = client.pods.create(
    client.models.V1Pod(
        metadata=client.models.V1ObjectMeta(name="busybox-composed-test"),
        spec=client.models.V1PodSpec(
            containers=[
                client.models.V1Container(
                    image="busybox",
                    args=["sleep", "9999999"],
                    name="busybox"
                )
            ]
        )
    ),
    namespace='default'
).first()
pod.wait()
print('pod create (composed):', pod)
assert pod.ready
pod.delete()


print('testing pod create by manifest')
pod = client.pods.create({
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': 'busybox-manifest-test'
        },
        'spec': {
            'containers': [
                {
                    'image': 'busybox',
                    'name': 'busybox',
                    "args": ["sleep", "9999999"]
                }
            ]
        }
    },
    namespace='default'
).first()
pod.wait()
print('pod create (manifest):', pod)
assert pod.ready
pod.delete()
print('pod deleted', pod)


print('testing pod get')
pods = client.pods.get()
print('num pods', len(pods.body))
assert len(pods.body) > 32


pod = pods.first()
print('pod', pod)
assert isinstance(pod, kubed.objects.api.resources.Pod)


first_ten_pods = pods.first(10)
print('num_pods first_ten', len(first_ten_pods))
assert len(first_ten_pods) == 10


print('creating pod for rest of tests')
pod = client.pods.create({
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': 'busybox'
        },
        'spec': {
            'containers': [
                {
                    'image': 'busybox',
                    'name': 'busybox',
                    "args": [
                        "/bin/ash",
                        "-c",
                        "while true; do echo $(date); sleep 2; done"
                    ]
                }
            ]
        }
    },
    namespace='default'
).first()
pod.wait()


print('testing pod patch (dict)')
pod.patch(dict(
    metadata=dict(
        labels=dict(
            fizz='buzz'
        )
    )
))
pod.reload()
assert pod.metadata.labels['fizz'] == 'buzz'


print('testing pod replace (composed)')
pod.spec.containers[0].image = 'busybox:1.26.1'
pod.replace()
pod.reload()
assert pod.spec.containers[0].image == 'busybox:1.26.1'


print('testing label')
pod.label(dict(new_key='new_value'))
pod.reload()
assert pod.metadata.labels['new_key'] == 'new_value'


print('testing annotate')
pod.annotate({'new.annotation.co/label': 'annotate-value'})
pod.reload()
assert pod.metadata.annotations['new.annotation.co/label'] == 'annotate-value'


print('testing label selectors')
pod = client.pods.get(selectors=dict(label=dict(fizz='buzz'))).first()
assert pod.metadata.labels['fizz'] == 'buzz'


print('testing field selectors')
pod = client.pods.get(selectors=dict(field={'metadata.name': 'busybox'})).first()
assert pod.metadata.name == 'busybox'


print('testing exec non-interactive')
pod = client.pods.get(name='busybox', namespace='default').first()
pod.exec(command='echo hello > ~/.hello', shell='/bin/ash')

response = pod.exec(command='cat ~/.hello').body.strip()
print(response)
assert response == 'hello'


print('testing exec interactive')
stream = pod.exec(shell='/bin/ash', interactive=True)
stdout, stderr = stream.execute('cat ~/.hello')
print(stdout, stderr)
assert stdout.strip() == 'hello'
stream.close()


print('testing watch')
pod_watch = client.pods.get(watch=True, timeout_seconds=5)
events = [event for event in pod_watch.stream()]
assert isinstance(events, list)
assert len(events) > 32


print('testing watch event')
event = events[0]
assert isinstance(event, kubed.rest.response.watch.WatchResponse.WatchEvent)
assert event.type in ('added', 'updated', 'deleted')
assert isinstance(event.obj, kubed.objects.api.resources.Pod)
assert isinstance(event.raw, dict)


print('testing pod logs')
pod = client.pods.get(namespace='default', selectors=dict(label=dict(app='couchdb'))).first()
logs = pod.logs(container='couchdb', since=timedelta(minutes=10))
assert getattr(logs, 'body', None)
assert len(logs.body.splitlines()) > 100


print('cleaning up')
client.pods.get(name='busybox', namespace='default').first().delete()


# MORE OBJECTS

print('testing node object')
node = client.nodes.get(name='jupiter.telephone.org').first()
assert node.ready is True
assert node.address == '162.210.194.99'
assert node.hostname == 'jupiter.telephone.org'


print('testing configmap data')
cm = client.config_maps.get(namespace='default', selectors=dict(label=dict(app='couchdb'))).first()
assert isinstance(cm, kubed.objects.api.resources.ConfigMap)
assert cm.get('erlang.hostname') == 'long'


print('testing secret data')
secret = client.secrets.get(namespace='default', selectors=dict(label=dict(app='couchdb'))).first()
assert isinstance(secret, kubed.objects.api.resources.Secret)
assert (hashlib.sha256(secret.data['user'].encode()).hexdigest() ==
        'a7a15d85c1d23d979076043f18f71f98f200085b92b6e21262f798d544906654')
print(secret)


print('testing endpoints')
ep = client.endpoints.get(namespace='default', selectors=dict(label=dict(app='rabbitmq'))).first()
for obj in [ep, ep._addresses, ep._targets, ep.nodes, ep.ips, ep.pods]:
    print(obj)
    assert obj


print('testing deployment')
dep = client.deployments.get(namespace='default', selectors=dict(label=dict(app='rabbitmq'))).first()
assert isinstance(dep, kubed.objects.api.resources.Deployment)
assert dep.ready == True
assert isinstance(dep.pods, list)
assert len(dep.pods) == 1


print('testing replicaset')
repset = client.replica_sets.get(namespace='default', selectors=dict(label=dict(app='rabbitmq'))).first()
assert isinstance(repset, kubed.objects.api.resources.ReplicaSet)
assert repset.ready == True
assert isinstance(repset.pods, list)
assert len(repset.pods) == 1


print('testing statefulsets')
ss = client.stateful_sets.get(namespace='default', selectors=dict(label=dict(app='couchdb'))).first()
assert isinstance(ss, kubed.objects.api.resources.StatefulSet)
assert ss.ready == True
assert isinstance(ss.pods, list)
assert len(ss.pods) == 3


print('testing daemonsets')
ds = client.daemon_sets.get(namespace='kube-system', selectors=dict(label={'k8s-app': 'calico-node'})).first()
assert isinstance(ds, kubed.objects.api.resources.DaemonSet)
assert ds.ready == True
assert isinstance(ds.pods, list)
assert len(ds.pods) == 3


print('testing ingress')
ing = client.ingresses.get(namespace='default', name='my.telephone.org').first()
print(ing)
assert isinstance(ing, kubed.objects.api.resources.Ingress)


print('testing namespace')
ns = client.namespaces.get(name='kube-system', namespace=None).first()
print(ns)
assert isinstance(ns, kubed.objects.api.resources.Namespace)


print('testing persistent volumes')
pv = client.persistent_volumes.get(namespace=None).first()
print(pv)
assert isinstance(pv, kubed.objects.api.resources.PersistentVolume)
assert pv.phase == 'Bound'
assert pv.bound == True
pvc = pv.claim
assert isinstance(pvc, kubed.objects.api.resources.PersistentVolumeClaim)


print('testing persistent volume claims')
pvc = client.persistent_volume_claims.get(namespace=None).first()
print(pvc)
assert isinstance(pvc, kubed.objects.api.resources.PersistentVolumeClaim)
assert pv.phase == 'Bound'
assert pv.bound == True
pv = pvc.volume
assert isinstance(pv, kubed.objects.api.resources.PersistentVolume)


print('testing service accounts')
sa = client.service_accounts.get(namespace=None).first()
print(sa)
assert isinstance(sa, kubed.objects.api.resources.ServiceAccount)


# FIRST PASS TESTING FOR LEADER ELECTION
from kubed.tools.leader_election import LeaderElection

identity = 'couchdb-1'
election = LeaderElection(
    client, name='couchdb', namespace='default', identity=identity)

with election:
    election.start()
    election.join()
