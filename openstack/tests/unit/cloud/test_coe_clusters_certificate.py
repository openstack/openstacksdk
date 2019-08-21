# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import munch

from openstack.tests.unit import base

coe_cluster_ca_obj = munch.Munch(
    cluster_uuid="43e305ce-3a5f-412a-8a14-087834c34c8c",
    pem="-----BEGIN CERTIFICATE-----\nMIIDAO\n-----END CERTIFICATE-----\n",
    bay_uuid="43e305ce-3a5f-412a-8a14-087834c34c8c",
    links=[]
)

coe_cluster_signed_cert_obj = munch.Munch(
    cluster_uuid='43e305ce-3a5f-412a-8a14-087834c34c8c',
    pem='-----BEGIN CERTIFICATE-----\nMIIDAO\n-----END CERTIFICATE-----',
    bay_uuid='43e305ce-3a5f-412a-8a14-087834c34c8c',
    links=[],
    csr=('-----BEGIN CERTIFICATE REQUEST-----\nMIICfz=='
         '\n-----END CERTIFICATE REQUEST-----\n')
)


class TestCOEClusters(base.TestCase):

    def get_mock_url(
            self,
            service_type='container-infrastructure-management',
            base_url_append=None, append=None, resource=None):
        return super(TestCOEClusters, self).get_mock_url(
            service_type=service_type, resource=resource,
            append=append, base_url_append=base_url_append)

    def test_get_coe_cluster_certificate(self):
        self.register_uris([dict(
            method='GET',
            uri=self.get_mock_url(
                resource='certificates',
                append=[coe_cluster_ca_obj.cluster_uuid]),
            json=coe_cluster_ca_obj)
        ])
        ca_cert = self.cloud.get_coe_cluster_certificate(
            coe_cluster_ca_obj.cluster_uuid)
        self.assertEqual(
            coe_cluster_ca_obj,
            ca_cert)
        self.assert_calls()

    def test_sign_coe_cluster_certificate(self):
        self.register_uris([dict(
            method='POST',
            uri=self.get_mock_url(resource='certificates'),
            json={"cluster_uuid": coe_cluster_signed_cert_obj.cluster_uuid,
                  "csr": coe_cluster_signed_cert_obj.csr}
        )])
        self.cloud.sign_coe_cluster_certificate(
            coe_cluster_signed_cert_obj.cluster_uuid,
            coe_cluster_signed_cert_obj.csr)
        self.assert_calls()
