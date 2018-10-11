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

from openstack.tests.unit import base

from openstack.clustering.v1 import cluster_attr as ca


FAKE = {
    'cluster_id': '633bd3c6-520b-420f-8e6a-dc2a47022b53',
    'path': 'path.to.attr',
    'id': 'c378e474-d091-43a3-b083-e19719291358',
    'value': 'fake value',
}


class TestClusterAttr(base.TestCase):

    def setUp(self):
        super(TestClusterAttr, self).setUp()

    def test_basic(self):
        sot = ca.ClusterAttr()
        self.assertEqual('cluster_attributes', sot.resources_key)
        self.assertEqual('/clusters/%(cluster_id)s/attrs/%(path)s',
                         sot.base_path)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = ca.ClusterAttr(**FAKE)
        self.assertEqual(FAKE['cluster_id'], sot.cluster_id)
        self.assertEqual(FAKE['path'], sot.path)
        self.assertEqual(FAKE['id'], sot.node_id)
        self.assertEqual(FAKE['value'], sot.attr_value)
