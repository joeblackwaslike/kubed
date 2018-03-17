from kubernetes.client.models.v1_api_group import V1APIGroup
from kubernetes.client.models.v1beta1_custom_resource_definition_status import \
    V1beta1CustomResourceDefinitionStatus

# tracking: https://github.com/kubernetes-incubator/client-python/issues/418
# let's hope to get expected behavior soon!
def fix_api_group_null_value():
    _server_address_by_client_cid_rs = V1APIGroup.server_address_by_client_cid_rs

    @_server_address_by_client_cid_rs.setter
    def _server_address_by_client_cid_rs(self, server_address_by_client_cid_rs):
        self._server_address_by_client_cid_rs = server_address_by_client_cid_rs

    V1APIGroup.server_address_by_client_cid_rs = _server_address_by_client_cid_rs


def fix_crd_status_conditions_null_value():
    _conditions = V1beta1CustomResourceDefinitionStatus.conditions

    @_conditions.setter
    def _conditions(self, conditions):
        self._conditions = conditions

    V1beta1CustomResourceDefinitionStatus.conditions = _conditions


def apply_all():
    fix_api_group_null_value()
    fix_crd_status_conditions_null_value()
