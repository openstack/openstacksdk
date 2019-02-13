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

import random

from openstack import exceptions
from openstack.tests.functional.baremetal import base


class TestBareMetalAllocation(base.BaseBaremetalTest):

    min_microversion = '1.52'

    def setUp(self):
        super(TestBareMetalAllocation, self).setUp()
        # NOTE(dtantsur): generate a unique resource class to prevent parallel
        # tests from clashing.
        self.resource_class = 'baremetal-%d' % random.randrange(1024)
        self.node = self._create_available_node()

    def _create_available_node(self):
        node = self.create_node(resource_class=self.resource_class)
        self.conn.baremetal.set_node_provision_state(node, 'manage',
                                                     wait=True)
        self.conn.baremetal.set_node_provision_state(node, 'provide',
                                                     wait=True)
        # Make sure the node has non-empty power state by forcing power off.
        self.conn.baremetal.set_node_power_state(node, 'power off')
        self.addCleanup(
            lambda: self.conn.baremetal.update_node(node.id,
                                                    instance_id=None))
        return node

    def test_allocation_create_get_delete(self):
        allocation = self.create_allocation(resource_class=self.resource_class)
        self.assertEqual('allocating', allocation.state)
        self.assertIsNone(allocation.node_id)
        self.assertIsNone(allocation.last_error)

        loaded = self.conn.baremetal.wait_for_allocation(allocation)
        self.assertEqual(loaded.id, allocation.id)
        self.assertEqual('active', allocation.state)
        self.assertEqual(self.node.id, allocation.node_id)
        self.assertIsNone(allocation.last_error)

        node = self.conn.baremetal.get_node(self.node.id)
        self.assertEqual(allocation.id, node.allocation_id)

        self.conn.baremetal.delete_allocation(allocation, ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_allocation, allocation.id)

    def test_allocation_list(self):
        allocation1 = self.create_allocation(
            resource_class=self.resource_class)
        allocation2 = self.create_allocation(
            resource_class=self.resource_class + '-fail')

        self.conn.baremetal.wait_for_allocation(allocation1)
        self.conn.baremetal.wait_for_allocation(allocation2, ignore_error=True)

        allocations = self.conn.baremetal.allocations()
        self.assertEqual({p.id for p in allocations},
                         {allocation1.id, allocation2.id})

        allocations = self.conn.baremetal.allocations(state='active')
        self.assertEqual([p.id for p in allocations], [allocation1.id])

        allocations = self.conn.baremetal.allocations(node=self.node.id)
        self.assertEqual([p.id for p in allocations], [allocation1.id])

        allocations = self.conn.baremetal.allocations(
            resource_class=self.resource_class + '-fail')
        self.assertEqual([p.id for p in allocations], [allocation2.id])

    def test_allocation_negative_failure(self):
        allocation = self.create_allocation(
            resource_class=self.resource_class + '-fail')
        self.assertRaises(exceptions.SDKException,
                          self.conn.baremetal.wait_for_allocation,
                          allocation)

        allocation = self.conn.baremetal.get_allocation(allocation.id)
        self.assertEqual('error', allocation.state)
        self.assertIn(self.resource_class + '-fail', allocation.last_error)

    def test_allocation_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_allocation, uuid)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.delete_allocation, uuid,
                          ignore_missing=False)
        self.assertIsNone(self.conn.baremetal.delete_allocation(uuid))

    def test_allocation_fields(self):
        self.create_allocation(resource_class=self.resource_class)
        result = self.conn.baremetal.allocations(fields=['uuid'])
        for item in result:
            self.assertIsNotNone(item.id)
            self.assertIsNone(item.resource_class)
