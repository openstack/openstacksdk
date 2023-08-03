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

from openstack.placement.v1 import trait as _trait
from openstack.tests.functional import base


class TestTrait(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.skipTest(
            "This test intermittently fails on DevStack deployments. "
            "See https://bugs.launchpad.net/placement/+bug/2029520 for more "
            "information."
        )

        if not self.operator_cloud.has_service('placement'):
            self.skipTest('placement service not supported by cloud')

        self.trait_name = f'CUSTOM_{uuid.uuid4().hex.upper()}'

        trait = self.operator_cloud.placement.create_trait(
            name=self.trait_name,
        )
        self.assertIsInstance(trait, _trait.Trait)
        self.assertEqual(self.trait_name, trait.name)

        self.trait = trait

    def tearDown(self):
        self.operator_cloud.placement.delete_trait(self.trait)
        super().tearDown()

    def test_resource_provider_inventory(self):
        # list all traits

        traits = list(self.operator_cloud.placement.traits())
        self.assertIsInstance(traits[0], _trait.Trait)
        self.assertIn(self.trait.name, {x.id for x in traits})

        # (no update_trait method)

        # retrieve details of the trait

        trait = self.operator_cloud.placement.get_trait(self.trait)
        self.assertIsInstance(trait, _trait.Trait)
        self.assertEqual(self.trait_name, trait.id)

        # retrieve details of the trait using IDs

        trait = self.operator_cloud.placement.get_trait(self.trait_name)
        self.assertIsInstance(trait, _trait.Trait)
        self.assertEqual(self.trait_name, trait.id)

        # (no find_trait method)
