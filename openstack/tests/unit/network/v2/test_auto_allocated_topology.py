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

from openstack.network.v2 import auto_allocated_topology

EXAMPLE = {
    'tenant_id': '1',
    'dry_run': False,
}


class TestAutoAllocatedTopology(base.TestCase):

    def test_basic(self):
        topo = auto_allocated_topology.AutoAllocatedTopology
        self.assertEqual('auto_allocated_topology', topo.resource_key)
        self.assertEqual('/auto-allocated-topology', topo.base_path)
        self.assertFalse(topo.allow_create)
        self.assertTrue(topo.allow_get)
        self.assertFalse(topo.allow_update)
        self.assertTrue(topo.allow_delete)
        self.assertFalse(topo.allow_list)

    def test_make_it(self):
        topo = auto_allocated_topology.AutoAllocatedTopology(**EXAMPLE)
        self.assertEqual(EXAMPLE['tenant_id'], topo.project_id)
