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


from openstack.container_infrastructure_management.v1 import cluster
from openstack.tests.unit import base


coe_cluster_obj = dict(
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
    def _compare_clusters(self, exp, real):
        self.assertDictEqual(
            cluster.Cluster(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def get_mock_url(
        self,
        service_type="container-infrastructure-management",
        base_url_append=None,
        append=None,
        resource=None,
    ):
        return super().get_mock_url(
            service_type=service_type,
            resource=resource,
            append=append,
            base_url_append=base_url_append,
        )

    def test_list_coe_clusters(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(resource="clusters"),
                    json=dict(clusters=[coe_cluster_obj]),
                )
            ]
        )
        cluster_list = self.cloud.list_coe_clusters()
        self._compare_clusters(
            coe_cluster_obj,
            cluster_list[0],
        )
        self.assert_calls()

    def test_create_coe_cluster(self):
        json_response = dict(uuid=coe_cluster_obj.get("uuid"))
        kwargs = dict(
            name=coe_cluster_obj["name"],
            cluster_template_id=coe_cluster_obj["cluster_template_id"],
            master_count=coe_cluster_obj["master_count"],
            node_count=coe_cluster_obj["node_count"],
        )
        self.register_uris(
            [
                dict(
                    method="POST",
                    uri=self.get_mock_url(resource="clusters"),
                    json=json_response,
                    validate=dict(json=kwargs),
                ),
            ]
        )
        response = self.cloud.create_coe_cluster(**kwargs)
        expected = kwargs.copy()
        expected.update(**json_response)
        self._compare_clusters(expected, response)
        self.assert_calls()

    def test_search_coe_cluster_by_name(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(resource="clusters"),
                    json=dict(clusters=[coe_cluster_obj]),
                )
            ]
        )

        coe_clusters = self.cloud.search_coe_clusters(name_or_id="k8s")

        self.assertEqual(1, len(coe_clusters))
        self.assertEqual(coe_cluster_obj["uuid"], coe_clusters[0]["id"])
        self.assert_calls()

    def test_search_coe_cluster_not_found(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(resource="clusters"),
                    json=dict(clusters=[coe_cluster_obj]),
                )
            ]
        )

        coe_clusters = self.cloud.search_coe_clusters(
            name_or_id="non-existent"
        )

        self.assertEqual(0, len(coe_clusters))
        self.assert_calls()

    def test_get_coe_cluster(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(resource="clusters"),
                    json=dict(clusters=[coe_cluster_obj]),
                )
            ]
        )

        r = self.cloud.get_coe_cluster(coe_cluster_obj["name"])
        self.assertIsNotNone(r)
        self._compare_clusters(
            coe_cluster_obj,
            r,
        )
        self.assert_calls()

    def test_get_coe_cluster_not_found(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(resource="clusters"),
                    json=dict(clusters=[]),
                )
            ]
        )
        r = self.cloud.get_coe_cluster("doesNotExist")
        self.assertIsNone(r)
        self.assert_calls()

    def test_delete_coe_cluster(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(resource="clusters"),
                    json=dict(clusters=[coe_cluster_obj]),
                ),
                dict(
                    method="DELETE",
                    uri=self.get_mock_url(
                        resource="clusters", append=[coe_cluster_obj['uuid']]
                    ),
                ),
            ]
        )
        self.cloud.delete_coe_cluster(coe_cluster_obj["uuid"])
        self.assert_calls()

    def test_update_coe_cluster(self):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.get_mock_url(resource="clusters"),
                    json=dict(clusters=[coe_cluster_obj]),
                ),
                dict(
                    method="PATCH",
                    uri=self.get_mock_url(
                        resource="clusters", append=[coe_cluster_obj["uuid"]]
                    ),
                    status_code=200,
                    validate=dict(
                        json=[
                            {
                                "op": "replace",
                                "path": "/node_count",
                                "value": 3,
                            }
                        ]
                    ),
                ),
            ]
        )
        self.cloud.update_coe_cluster(coe_cluster_obj["uuid"], node_count=3)
        self.assert_calls()
