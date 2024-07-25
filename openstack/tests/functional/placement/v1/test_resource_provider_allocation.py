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

import uuid

from openstack.placement.v1 import resource_class as _resource_class
from openstack.placement.v1 import resource_provider as _resource_provider
from openstack.placement.v1 import (
    resource_provider_allocation as _resource_provider_allocation,
)
from openstack.placement.v1 import (
    resource_provider_inventory as _resource_provider_inventory,
)
from openstack.tests.functional import base


class TestResourceProviderAllocation(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud.has_service('placement'):
            self.skipTest('placement service not supported by cloud')

        self.resource_provider_name = self.getUniqueString()
        self.resource_class_name = f'CUSTOM_{uuid.uuid4().hex.upper()}'
        self.consumer_id = str(uuid.uuid4())
        self.project_id = self.operator_cloud.current_project_id
        self.user_id = self.operator_cloud.current_user_id

        # create resource class
        resource_class = self.operator_cloud.placement.create_resource_class(
            name=self.resource_class_name,
        )
        self.assertIsInstance(resource_class, _resource_class.ResourceClass)
        self.assertEqual(self.resource_class_name, resource_class.name)

        # create resource provider
        resource_provider = (
            self.operator_cloud.placement.create_resource_provider(
                name=self.resource_provider_name,
            )
        )
        self.assertIsInstance(
            resource_provider,
            _resource_provider.ResourceProvider,
        )
        self.assertEqual(self.resource_provider_name, resource_provider.name)

        # create resource provider inventory
        resource_provider_inventory = (
            self.operator_cloud.placement.create_resource_provider_inventory(
                resource_provider,
                resource_class=resource_class,
                total=10,
                step_size=1,
            )
        )
        self.assertIsInstance(
            resource_provider_inventory,
            _resource_provider_inventory.ResourceProviderInventory,
        )
        self.assertEqual(
            self.resource_class_name,
            resource_provider_inventory.resource_class,
        )
        self.assertEqual(10, resource_provider_inventory.total)

        self.resource_provider = resource_provider
        self.resource_class = resource_class
        self.resource_provider_inventory = resource_provider_inventory

        # create allocation for the consumer
        self.operator_cloud.placement.update_allocation(
            self.consumer_id,
            allocations={
                self.resource_provider.id: {
                    'resources': {self.resource_class_name: 1},
                },
            },
            project_id=self.project_id,
            user_id=self.user_id,
            consumer_generation=None,
            consumer_type='INSTANCE',
        )

    def tearDown(self):
        # allocation must be removed before the resource provider can be
        # deleted
        self.operator_cloud.placement.delete_allocation(
            self.consumer_id,
            ignore_missing=True,
        )
        self.operator_cloud.placement.delete_resource_provider(
            self.resource_provider,
        )
        self.operator_cloud.placement.delete_resource_class(
            self.resource_class,
        )
        super().tearDown()

    def test_resource_provider_allocation(self):
        # list all resource provider allocations (there should only be one)

        resource_provider_allocations = list(
            self.operator_cloud.placement.resource_provider_allocations(
                self.resource_provider
            )
        )
        self.assertEqual(1, len(resource_provider_allocations))
        self.assertIsInstance(
            resource_provider_allocations[0],
            _resource_provider_allocation.ResourceProviderAllocation,
        )
        self.assertEqual(self.consumer_id, resource_provider_allocations[0].id)
        self.assertIn(
            self.resource_class_name,
            resource_provider_allocations[0].resources,
        )
