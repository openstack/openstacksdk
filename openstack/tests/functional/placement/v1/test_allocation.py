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

from openstack.placement.v1 import allocation as _allocation
from openstack.placement.v1 import resource_class as _resource_class
from openstack.placement.v1 import resource_provider as _resource_provider
from openstack.tests.functional import base


class TestAllocation(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud.has_service('placement'):
            self.skipTest('placement service not supported by cloud')

        self.resource_provider_name = self.getUniqueString()
        self.resource_class_name = f'CUSTOM_{uuid.uuid4().hex.upper()}'
        self.consumer_id = str(uuid.uuid4())
        self.project_id = self.operator_cloud.current_project_id
        self.user_id = self.operator_cloud.current_user_id

        resource_class = self.operator_cloud.placement.create_resource_class(
            name=self.resource_class_name,
        )
        self.assertIsInstance(resource_class, _resource_class.ResourceClass)

        resource_provider = (
            self.operator_cloud.placement.create_resource_provider(
                name=self.resource_provider_name,
            )
        )
        self.assertIsInstance(
            resource_provider,
            _resource_provider.ResourceProvider,
        )

        self.operator_cloud.placement.create_resource_provider_inventory(
            resource_provider,
            resource_class=resource_class,
            total=100,
        )

        self.resource_provider = resource_provider
        self.resource_class = resource_class

    def tearDown(self):
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

    def test_allocation(self):
        # create allocations for the consumer via update (PUT)
        # consumer_generation=None signals the consumer does not yet exist;
        # consumer_type is required from microversion 1.38 onwards.

        alloc = self.operator_cloud.placement.update_allocation(
            self.consumer_id,
            allocations={
                self.resource_provider.id: {
                    'resources': {self.resource_class_name: 10},
                },
            },
            project_id=self.project_id,
            user_id=self.user_id,
            consumer_generation=None,
            consumer_type='INSTANCE',
        )
        self.assertIsInstance(alloc, _allocation.Allocation)

        # retrieve allocations for the consumer

        alloc = self.operator_cloud.placement.get_allocation(self.consumer_id)
        self.assertIsInstance(alloc, _allocation.Allocation)
        self.assertIn(self.resource_provider.id, alloc.allocations)
        self.assertEqual(
            {self.resource_class_name: 10},
            alloc.allocations[self.resource_provider.id]['resources'],
        )

        # update the allocations; use the consumer_generation fetched above so
        # the server can detect concurrent modifications.

        alloc = self.operator_cloud.placement.update_allocation(
            self.consumer_id,
            allocations={
                self.resource_provider.id: {
                    'resources': {self.resource_class_name: 20},
                },
            },
            project_id=self.project_id,
            user_id=self.user_id,
            consumer_generation=alloc.consumer_generation,
            consumer_type='INSTANCE',
        )
        self.assertIsInstance(alloc, _allocation.Allocation)

        # verify the update

        alloc = self.operator_cloud.placement.get_allocation(self.consumer_id)
        self.assertEqual(
            {self.resource_class_name: 20},
            alloc.allocations[self.resource_provider.id]['resources'],
        )

        # delete the allocations

        result = self.operator_cloud.placement.delete_allocation(
            self.consumer_id,
            ignore_missing=False,
        )
        self.assertIsNone(result)

        # re-create via the batch endpoint (POST /allocations), which sets
        # allocations for multiple consumers atomically; consumer_generation
        # must be null when the consumer does not yet exist.

        result = self.operator_cloud.placement.create_allocations(
            allocations={
                self.consumer_id: {
                    'allocations': {
                        self.resource_provider.id: {
                            'resources': {self.resource_class_name: 5},
                        },
                    },
                    'project_id': self.project_id,
                    'user_id': self.user_id,
                    'consumer_generation': None,
                    'consumer_type': 'INSTANCE',
                },
            },
        )
        self.assertIsNone(result)

        alloc = self.operator_cloud.placement.get_allocation(self.consumer_id)
        self.assertEqual(
            {self.resource_class_name: 5},
            alloc.allocations[self.resource_provider.id]['resources'],
        )
