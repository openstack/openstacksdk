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


class Base(base.BaseBaremetalTest):
    def setUp(self):
        super().setUp()
        # NOTE(dtantsur): generate a unique resource class to prevent parallel
        # tests from clashing.
        self.resource_class = f'baremetal-{random.randrange(1024)}'
        self.node = self._create_available_node()

    def _create_available_node(self):
        node = self.create_node(resource_class=self.resource_class)
        self.operator_cloud.baremetal.set_node_provision_state(
            node, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_provision_state(
            node, 'provide', wait=True
        )
        # Make sure the node has non-empty power state by forcing power off.
        self.operator_cloud.baremetal.set_node_power_state(node, 'power off')
        self.addCleanup(
            lambda: self.operator_cloud.baremetal.update_node(
                node.id, instance_id=None
            )
        )
        return node


class TestBareMetalAllocation(Base):
    min_microversion = '1.52'

    def test_allocation_create_get_delete(self):
        allocation = self.create_allocation(resource_class=self.resource_class)
        self.assertEqual('allocating', allocation.state)
        self.assertIsNone(allocation.node_id)
        self.assertIsNone(allocation.last_error)

        loaded = self.operator_cloud.baremetal.wait_for_allocation(allocation)
        self.assertEqual(loaded.id, allocation.id)
        self.assertEqual('active', allocation.state)
        self.assertEqual(self.node.id, allocation.node_id)
        self.assertIsNone(allocation.last_error)

        with_fields = self.operator_cloud.baremetal.get_allocation(
            allocation.id, fields=['uuid', 'node_uuid']
        )
        self.assertEqual(allocation.id, with_fields.id)
        self.assertIsNone(with_fields.state)

        node = self.operator_cloud.baremetal.get_node(self.node.id)
        self.assertEqual(allocation.id, node.allocation_id)

        self.operator_cloud.baremetal.delete_allocation(
            allocation, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_allocation,
            allocation.id,
        )

    def test_allocation_list(self):
        allocation1 = self.create_allocation(
            resource_class=self.resource_class
        )
        allocation2 = self.create_allocation(
            resource_class=self.resource_class + '-fail'
        )

        self.operator_cloud.baremetal.wait_for_allocation(allocation1)
        self.operator_cloud.baremetal.wait_for_allocation(
            allocation2, ignore_error=True
        )

        allocations = self.operator_cloud.baremetal.allocations()
        self.assertEqual(
            {p.id for p in allocations}, {allocation1.id, allocation2.id}
        )

        allocations = self.operator_cloud.baremetal.allocations(state='active')
        self.assertEqual([p.id for p in allocations], [allocation1.id])

        allocations = self.operator_cloud.baremetal.allocations(
            node=self.node.id
        )
        self.assertEqual([p.id for p in allocations], [allocation1.id])

        allocations = self.operator_cloud.baremetal.allocations(
            resource_class=self.resource_class + '-fail'
        )
        self.assertEqual([p.id for p in allocations], [allocation2.id])

    def test_allocation_negative_failure(self):
        allocation = self.create_allocation(
            resource_class=self.resource_class + '-fail'
        )
        self.assertRaises(
            exceptions.SDKException,
            self.operator_cloud.baremetal.wait_for_allocation,
            allocation,
        )

        allocation = self.operator_cloud.baremetal.get_allocation(
            allocation.id
        )
        self.assertEqual('error', allocation.state)
        self.assertIn(self.resource_class + '-fail', allocation.last_error)

    def test_allocation_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_allocation,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.delete_allocation,
            uuid,
            ignore_missing=False,
        )
        self.assertIsNone(
            self.operator_cloud.baremetal.delete_allocation(uuid)
        )

    def test_allocation_fields(self):
        self.create_allocation(resource_class=self.resource_class)
        result = self.operator_cloud.baremetal.allocations(fields=['uuid'])
        for item in result:
            self.assertIsNotNone(item.id)
            self.assertIsNone(item.resource_class)


class TestBareMetalAllocationUpdate(Base):
    min_microversion = '1.57'

    def test_allocation_update(self):
        name = 'ossdk-name1'

        allocation = self.create_allocation(resource_class=self.resource_class)
        allocation = self.operator_cloud.baremetal.wait_for_allocation(
            allocation
        )
        self.assertEqual('active', allocation.state)
        self.assertIsNone(allocation.last_error)
        self.assertIsNone(allocation.name)
        self.assertEqual({}, allocation.extra)

        allocation = self.operator_cloud.baremetal.update_allocation(
            allocation, name=name, extra={'answer': 42}
        )
        self.assertEqual(name, allocation.name)
        self.assertEqual({'answer': 42}, allocation.extra)

        allocation = self.operator_cloud.baremetal.get_allocation(name)
        self.assertEqual(name, allocation.name)
        self.assertEqual({'answer': 42}, allocation.extra)

        self.operator_cloud.baremetal.delete_allocation(
            allocation, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_allocation,
            allocation.id,
        )

    def test_allocation_patch(self):
        name = 'ossdk-name2'

        allocation = self.create_allocation(resource_class=self.resource_class)
        allocation = self.operator_cloud.baremetal.wait_for_allocation(
            allocation
        )
        self.assertEqual('active', allocation.state)
        self.assertIsNone(allocation.last_error)
        self.assertIsNone(allocation.name)
        self.assertEqual({}, allocation.extra)

        allocation = self.operator_cloud.baremetal.patch_allocation(
            allocation,
            [
                {'op': 'replace', 'path': '/name', 'value': name},
                {'op': 'add', 'path': '/extra/answer', 'value': 42},
            ],
        )
        self.assertEqual(name, allocation.name)
        self.assertEqual({'answer': 42}, allocation.extra)

        allocation = self.operator_cloud.baremetal.get_allocation(name)
        self.assertEqual(name, allocation.name)
        self.assertEqual({'answer': 42}, allocation.extra)

        allocation = self.operator_cloud.baremetal.patch_allocation(
            allocation,
            [
                {'op': 'remove', 'path': '/name'},
                {'op': 'remove', 'path': '/extra/answer'},
            ],
        )
        self.assertIsNone(allocation.name)
        self.assertEqual({}, allocation.extra)

        allocation = self.operator_cloud.baremetal.get_allocation(
            allocation.id
        )
        self.assertIsNone(allocation.name)
        self.assertEqual({}, allocation.extra)

        self.operator_cloud.baremetal.delete_allocation(
            allocation, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_allocation,
            allocation.id,
        )
