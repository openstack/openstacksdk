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

import time

from openstack.clustering.v1 import cluster
from openstack.tests.functional import base
from openstack.tests.functional.network.v2 import test_network


class TestCluster(base.BaseFunctionalTest):
    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_CLUSTER'

    def setUp(self):
        super().setUp()
        self.require_service('clustering')

        self.cidr = '10.99.99.0/16'

        self.network, self.subnet = test_network.create_network(
            self.operator_cloud, self.getUniqueString(), self.cidr
        )
        self.assertIsNotNone(self.network)

        profile_attrs = {
            'name': self.getUniqueString(),
            'spec': {
                'type': 'os.nova.server',
                'version': 1.0,
                'properties': {
                    'name': self.getUniqueString(),
                    'flavor': self.flavor.name,
                    'image': self.image.name,
                    'networks': [{'network': self.network.id}],
                },
            },
        }

        self.profile = self.operator_cloud.clustering.create_profile(
            **profile_attrs
        )
        self.assertIsNotNone(self.profile)

        self.cluster_name = self.getUniqueString()
        cluster_spec = {
            "name": self.cluster_name,
            "profile_id": self.profile.name,
            "min_size": 0,
            "max_size": -1,
            "desired_capacity": 0,
        }

        self.cluster = self.operator_cloud.clustering.create_cluster(
            **cluster_spec
        )
        self.operator_cloud.clustering.wait_for_status(
            self.cluster, 'ACTIVE', wait=self._wait_for_timeout
        )
        assert isinstance(self.cluster, cluster.Cluster)

    def tearDown(self):
        if self.cluster:
            self.operator_cloud.clustering.delete_cluster(self.cluster.id)
            self.operator_cloud.clustering.wait_for_delete(
                self.cluster, wait=self._wait_for_timeout
            )

        test_network.delete_network(
            self.operator_cloud, self.network, self.subnet
        )

        self.operator_cloud.clustering.delete_profile(self.profile)

        super().tearDown()

    def test_find(self):
        sot = self.operator_cloud.clustering.find_cluster(self.cluster.id)
        self.assertEqual(self.cluster.id, sot.id)

    def test_get(self):
        sot = self.operator_cloud.clustering.get_cluster(self.cluster)
        self.assertEqual(self.cluster.id, sot.id)

    def test_list(self):
        names = [o.name for o in self.operator_cloud.clustering.clusters()]
        self.assertIn(self.cluster_name, names)

    def test_update(self):
        new_cluster_name = self.getUniqueString()
        sot = self.operator_cloud.clustering.update_cluster(
            self.cluster, name=new_cluster_name, profile_only=False
        )

        time.sleep(2)
        sot = self.operator_cloud.clustering.get_cluster(self.cluster)
        self.assertEqual(new_cluster_name, sot.name)

    def test_delete(self):
        cluster_delete_action = self.operator_cloud.clustering.delete_cluster(
            self.cluster.id
        )

        self.operator_cloud.clustering.wait_for_delete(
            self.cluster, wait=self._wait_for_timeout
        )

        action = self.operator_cloud.clustering.get_action(
            cluster_delete_action.id
        )
        self.assertEqual(action.target_id, self.cluster.id)
        self.assertEqual(action.action, 'CLUSTER_DELETE')
        self.assertEqual(action.status, 'SUCCEEDED')

        self.cluster = None

    def test_force_delete(self):
        cluster_delete_action = self.operator_cloud.clustering.delete_cluster(
            self.cluster.id, False, True
        )

        self.operator_cloud.clustering.wait_for_delete(
            self.cluster, wait=self._wait_for_timeout
        )

        action = self.operator_cloud.clustering.get_action(
            cluster_delete_action.id
        )
        self.assertEqual(action.target_id, self.cluster.id)
        self.assertEqual(action.action, 'CLUSTER_DELETE')
        self.assertEqual(action.status, 'SUCCEEDED')

        self.cluster = None
