from kubernetes.client.models.v1_api_group import V1APIGroup


# tracking: https://github.com/kubernetes-incubator/client-python/issues/418
# let's hope to get expected behavior soon!
def fix_api_group_null_value():
    _server_address_by_client_cid_rs = V1APIGroup.server_address_by_client_cid_rs

    @_server_address_by_client_cid_rs.setter
    def _server_address_by_client_cid_rs(self, server_address_by_client_cid_rs):
        self._server_address_by_client_cid_rs = server_address_by_client_cid_rs

    V1APIGroup.server_address_by_client_cid_rs = _server_address_by_client_cid_rs
