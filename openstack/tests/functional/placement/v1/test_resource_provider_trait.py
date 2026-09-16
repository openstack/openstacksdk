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

from openstack.placement.v1 import resource_provider as _resource_provider
from openstack.placement.v1 import resource_provider_trait as _rp_trait
from openstack.tests.functional import base


class TestResourceProviderTrait(base.BaseFunctionalTest):
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
        self.resource_provider = resource_provider

    def tearDown(self):
        self.operator_cloud.placement.delete_resource_provider_trait(
            self.resource_provider,
            ignore_missing=True,
        )
        self.operator_cloud.placement.delete_resource_provider(
            self.resource_provider,
        )
        super().tearDown()

    def test_resource_provider_trait(self):
        # retrieve traits for the resource provider (initially empty)

        rp_trait = self.operator_cloud.placement.get_resource_provider_trait(
            self.resource_provider
        )
        self.assertIsInstance(rp_trait, _rp_trait.ResourceProviderTrait)
        self.assertEqual([], rp_trait.traits)

        # associate traits with the resource provider

        rp_trait = self.operator_cloud.placement.set_resource_provider_trait(
            rp_trait,
            traits=['COMPUTE_STATUS_DISABLED'],
            resource_provider_generation=rp_trait.resource_provider_generation,
        )
        self.assertIsInstance(rp_trait, _rp_trait.ResourceProviderTrait)
        self.assertIn('COMPUTE_STATUS_DISABLED', rp_trait.traits)

        # retrieve traits again to confirm

        rp_trait = self.operator_cloud.placement.get_resource_provider_trait(
            self.resource_provider
        )
        self.assertIn('COMPUTE_STATUS_DISABLED', rp_trait.traits)

        # dissociate all traits from the resource provider

        result = self.operator_cloud.placement.delete_resource_provider_trait(
            self.resource_provider,
            ignore_missing=False,
        )
        self.assertIsNone(result)

        # verify traits are gone

        rp_trait = self.operator_cloud.placement.get_resource_provider_trait(
            self.resource_provider
        )
        self.assertEqual([], rp_trait.traits)
