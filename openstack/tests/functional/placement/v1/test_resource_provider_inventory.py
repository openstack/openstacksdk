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
    resource_provider_inventory as _resource_provider_inventory,
)
from openstack.tests.functional import base


class TestResourceProviderInventory(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud.has_service('placement'):
            self.skipTest('placement service not supported by cloud')

        self.resource_provider_name = self.getUniqueString()
        self.resource_class_name = f'CUSTOM_{uuid.uuid4().hex.upper()}'

        resource_class = self.operator_cloud.placement.create_resource_class(
            name=self.resource_class_name,
        )
        self.assertIsInstance(resource_class, _resource_class.ResourceClass)
        self.assertEqual(self.resource_class_name, resource_class.name)

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

        self.resource_provider = resource_provider
        self.resource_class = resource_class

    def tearDown(self):
        self.operator_cloud.placement.delete_resource_provider(
            self.resource_provider,
        )
        self.operator_cloud.placement.delete_resource_class(
            self.resource_class,
        )
        super().tearDown()

    def test_resource_provider_inventory(self):
        # create the resource provider inventory

        resource_provider_inventory = (
            self.operator_cloud.placement.create_resource_provider_inventory(
                self.resource_provider,
                resource_class=self.resource_class,
                total=10,
                step_size=1,
            )
        )
        self.assertIsInstance(
            resource_provider_inventory,
            _resource_provider_inventory.ResourceProviderInventory,
        )
        self.assertEqual(
            self.resource_class.name,
            resource_provider_inventory.resource_class,
        )
        self.assertEqual(10, resource_provider_inventory.total)

        # list all resource provider inventories (there should only be one)

        resource_provider_inventories = list(
            self.operator_cloud.placement.resource_provider_inventories(
                self.resource_provider
            )
        )
        self.assertIsInstance(
            resource_provider_inventories[0],
            _resource_provider_inventory.ResourceProviderInventory,
        )
        self.assertIn(
            self.resource_class.name,
            {rpi.id for rpi in resource_provider_inventories},
        )

        # update the resource provider inventory

        resource_provider_inventory = self.operator_cloud.placement.update_resource_provider_inventory(
            resource_provider_inventory,
            total=20,
            resource_provider_generation=resource_provider_inventory.resource_provider_generation,
        )
        self.assertIsInstance(
            resource_provider_inventory,
            _resource_provider_inventory.ResourceProviderInventory,
        )
        self.assertEqual(
            self.resource_class.name,
            resource_provider_inventory.id,
        )
        self.assertEqual(20, resource_provider_inventory.total)

        # retrieve details of the (updated) resource provider inventory

        resource_provider_inventory = (
            self.operator_cloud.placement.get_resource_provider_inventory(
                resource_provider_inventory,
            )
        )
        self.assertIsInstance(
            resource_provider_inventory,
            _resource_provider_inventory.ResourceProviderInventory,
        )
        self.assertEqual(
            self.resource_class.name,
            resource_provider_inventory.id,
        )
        self.assertEqual(20, resource_provider_inventory.total)

        # retrieve details of the resource provider inventory using IDs
        # (requires us to provide the resource provider also)

        resource_provider_inventory = (
            self.operator_cloud.placement.get_resource_provider_inventory(
                resource_provider_inventory.id,
                self.resource_provider,
            )
        )
        self.assertIsInstance(
            resource_provider_inventory,
            _resource_provider_inventory.ResourceProviderInventory,
        )
        self.assertEqual(
            self.resource_class.name,
            resource_provider_inventory.id,
        )
        self.assertEqual(20, resource_provider_inventory.total)

        # (no find_resource_provider_inventory method)

        # delete the resource provider inventory

        result = (
            self.operator_cloud.placement.delete_resource_provider_inventory(
                resource_provider_inventory,
                self.resource_provider,
                ignore_missing=False,
            )
        )
        self.assertIsNone(result)
