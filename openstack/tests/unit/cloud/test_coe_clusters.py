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

coe_cluster_obj = munch.Munch(
    status="CREATE_IN_PROGRESS",
    cluster_template_id="0562d357-8641-4759-8fed-8173f02c9633",
    uuid="731387cf-a92b-4c36-981e-3271d63e5597",
    links=[{}, {}],
    stack_id="31c1ee6c-081e-4f39-9f0f-f1d87a7defa1",
    keypair="my_keypair",
    master_count=3,
    create_timeout=60,
    node_count=10,
    name="k8s",
    created_at="2016-08-29T06:51:31+00:00",
    api_address="https://172.24.4.6:6443",
    discovery_url="https://discovery.etcd.io/cbeb580da58915809d59ee69348a84f3",
    updated_at="2016-08-29T06:53:24+00:00",
    coe_version="v1.2.0",
    master_addresses=["172.24.4.6"],
    node_addresses=["172.24.4.13"],
    status_reason="Stack CREATE completed successfully",
)


class TestCOEClusters(base.TestCase):

    def test_list_coe_clusters(self):

        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/clusters',
            json=dict(clusters=[coe_cluster_obj.toDict()]))])
        cluster_list = self.cloud.list_coe_clusters()
        self.assertEqual(
            cluster_list[0],
            self.cloud._normalize_coe_cluster(coe_cluster_obj))
        self.assert_calls()

    def test_create_coe_cluster(self):
        self.register_uris([dict(
            method='POST',
            uri='https://container-infra.example.com/v1/clusters',
            json=dict(baymodels=[coe_cluster_obj.toDict()]),
            validate=dict(json={
                'name': 'k8s',
                'cluster_template_id': '0562d357-8641-4759-8fed-8173f02c9633',
                'master_count': 3,
                'node_count': 10}),
        )])
        self.cloud.create_coe_cluster(
            name=coe_cluster_obj.name,
            cluster_template_id=coe_cluster_obj.cluster_template_id,
            master_count=coe_cluster_obj.master_count,
            node_count=coe_cluster_obj.node_count)
        self.assert_calls()

    def test_search_coe_cluster_by_name(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/clusters',
            json=dict(clusters=[coe_cluster_obj.toDict()]))])

        coe_clusters = self.cloud.search_coe_clusters(
            name_or_id='k8s')

        self.assertEqual(1, len(coe_clusters))
        self.assertEqual(coe_cluster_obj.uuid, coe_clusters[0]['id'])
        self.assert_calls()

    def test_search_coe_cluster_not_found(self):

        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/clusters',
            json=dict(clusters=[coe_cluster_obj.toDict()]))])

        coe_clusters = self.cloud.search_coe_clusters(
            name_or_id='non-existent')

        self.assertEqual(0, len(coe_clusters))
        self.assert_calls()

    def test_get_coe_cluster(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/clusters',
            json=dict(clusters=[coe_cluster_obj.toDict()]))])

        r = self.cloud.get_coe_cluster(coe_cluster_obj.name)
        self.assertIsNotNone(r)
        self.assertDictEqual(
            r, self.cloud._normalize_coe_cluster(coe_cluster_obj))
        self.assert_calls()

    def test_get_coe_cluster_not_found(self):
        self.register_uris([dict(
            method='GET',
            uri='https://container-infra.example.com/v1/clusters',
            json=dict(clusters=[]))])
        r = self.cloud.get_coe_cluster('doesNotExist')
        self.assertIsNone(r)
        self.assert_calls()

    def test_delete_coe_cluster(self):
        uri = ('https://container-infra.example.com/v1/clusters/%s' %
               coe_cluster_obj.uuid)
        self.register_uris([
            dict(
                method='GET',
                uri='https://container-infra.example.com/v1/clusters',
                json=dict(clusters=[coe_cluster_obj.toDict()])),
            dict(
                method='DELETE',
                uri=uri),
        ])
        self.cloud.delete_coe_cluster(coe_cluster_obj.uuid)
        self.assert_calls()

    def test_update_coe_cluster(self):
        uri = ('https://container-infra.example.com/v1/clusters/%s' %
               coe_cluster_obj.uuid)
        self.register_uris([
            dict(
                method='GET',
                uri='https://container-infra.example.com/v1/clusters',
                json=dict(clusters=[coe_cluster_obj.toDict()])),
            dict(
                method='PATCH',
                uri=uri,
                status_code=200,
                validate=dict(
                    json=[{
                        u'op': u'replace',
                        u'path': u'/node_count',
                        u'value': 3
                    }]
                )),
            dict(
                method='GET',
                uri='https://container-infra.example.com/v1/clusters',
                # This json value is not meaningful to the test - it just has
                # to be valid.
                json=dict(clusters=[coe_cluster_obj.toDict()])),
        ])
        self.cloud.update_coe_cluster(
            coe_cluster_obj.uuid, 'replace', node_count=3)
        self.assert_calls()
