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

EXAMPLE = {
    "cluster_template_id": "0562d357-8641-4759-8fed-8173f02c9633",
    "create_timeout": 60,
    "discovery_url": None,
    "flavor_id": None,
    "keypair": "my_keypair",
    "labels": {},
    "master_count": 2,
    "master_flavor_id": None,
    "name": "k8s",
    "node_count": 2,
}


class TestCluster(base.TestCase):
    def test_basic(self):
        sot = cluster.Cluster()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('clusters', sot.resources_key)
        self.assertEqual('/clusters', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = cluster.Cluster(**EXAMPLE)
        self.assertEqual(
            EXAMPLE['cluster_template_id'],
            sot.cluster_template_id,
        )
        self.assertEqual(EXAMPLE['create_timeout'], sot.create_timeout)
        self.assertEqual(EXAMPLE['discovery_url'], sot.discovery_url)
        self.assertEqual(EXAMPLE['flavor_id'], sot.flavor_id)
        self.assertEqual(EXAMPLE['keypair'], sot.keypair)
        self.assertEqual(EXAMPLE['labels'], sot.labels)
        self.assertEqual(EXAMPLE['master_count'], sot.master_count)
        self.assertEqual(EXAMPLE['master_flavor_id'], sot.master_flavor_id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['node_count'], sot.node_count)
