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

from openstack.placement.v1 import resource_provider as _resource_provider
from openstack.tests.functional import base


class TestResourceProvider(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud.has_service('placement'):
            self.skipTest('placement service not supported by cloud')

        self.resource_provider_name = self.getUniqueString()

        resource_provider = (
            self.operator_cloud.placement.create_resource_provider(
                name=self.resource_provider_name,
            )
        )
        self.assertIsInstance(
            resource_provider, _resource_provider.ResourceProvider
        )
        self.assertEqual(self.resource_provider_name, resource_provider.name)
        self.resource_provider = resource_provider

    def tearDown(self):
        result = self.operator_cloud.placement.delete_resource_provider(
            self.resource_provider,
        )
        self.assertIsNone(result)
        super().tearDown()

    def test_resource_provider(self):
        # list all resource providers

        resource_providers = list(
            self.operator_cloud.placement.resource_providers()
        )
        self.assertIsInstance(
            resource_providers[0],
            _resource_provider.ResourceProvider,
        )
        self.assertIn(
            self.resource_provider_name,
            {x.name for x in resource_providers},
        )

        # retrieve details of the resource provider by name

        resource_provider = (
            self.operator_cloud.placement.find_resource_provider(
                self.resource_provider.name,
            )
        )
        self.assertEqual(self.resource_provider_name, resource_provider.name)

        # retrieve details of the resource provider by ID

        resource_provider = (
            self.operator_cloud.placement.get_resource_provider(
                self.resource_provider.id,
            )
        )
        self.assertEqual(self.resource_provider_name, resource_provider.name)

        # update the resource provider

        new_resource_provider_name = self.getUniqueString()

        resource_provider = (
            self.operator_cloud.placement.update_resource_provider(
                self.resource_provider,
                name=new_resource_provider_name,
                generation=self.resource_provider.generation,
            )
        )
        self.assertIsInstance(
            resource_provider,
            _resource_provider.ResourceProvider,
        )
        self.assertEqual(
            new_resource_provider_name,
            resource_provider.name,
        )

    def test_resource_provider_aggregates(self):
        aggregates = [uuid.uuid4().hex, uuid.uuid4().hex]

        # update the resource provider aggregates

        resource_provider = (
            self.operator_cloud.placement.set_resource_provider_aggregates(
                self.resource_provider,
                *aggregates,
            )
        )
        self.assertCountEqual(aggregates, resource_provider.aggregates)

        # retrieve details of resource provider aggregates

        resource_provider = (
            self.operator_cloud.placement.get_resource_provider_aggregates(
                self.resource_provider,
            )
        )
        self.assertCountEqual(aggregates, resource_provider.aggregates)
