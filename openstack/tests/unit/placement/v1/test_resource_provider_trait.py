# Copyright 2026 SoftBank corp.
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.placement.v1 import resource_provider_trait
from openstack.tests.unit import base

FAKE = {
    'resource_provider_generation': 8,
    'traits': ['COMPUTE_IMAGE_TYPE_ISO', 'CUSTOM_TRAIT'],
}


class TestResourceProviderTrait(base.TestCase):
    def test_basic(self):
        sot = resource_provider_trait.ResourceProviderTrait()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual(
            '/resource_providers/%(resource_provider_id)s/traits',
            sot.base_path,
        )
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_patch)

        self.assertDictEqual({}, sot._query_mapping._mapping)

    def test_make_it(self):
        sot = resource_provider_trait.ResourceProviderTrait(**FAKE)
        self.assertEqual(
            FAKE['resource_provider_generation'],
            sot.resource_provider_generation,
        )
        self.assertEqual(FAKE['traits'], sot.traits)
