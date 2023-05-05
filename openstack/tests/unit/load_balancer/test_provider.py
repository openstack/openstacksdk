# Copyright 2019 Rackspace, US Inc.
#
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

from openstack.load_balancer.v2 import provider
from openstack.tests.unit import base


EXAMPLE = {'name': 'best', 'description': 'The best provider'}


class TestProvider(base.TestCase):
    def test_basic(self):
        test_provider = provider.Provider()
        self.assertEqual('providers', test_provider.resources_key)
        self.assertEqual('/lbaas/providers', test_provider.base_path)
        self.assertFalse(test_provider.allow_create)
        self.assertFalse(test_provider.allow_fetch)
        self.assertFalse(test_provider.allow_commit)
        self.assertFalse(test_provider.allow_delete)
        self.assertTrue(test_provider.allow_list)

    def test_make_it(self):
        test_provider = provider.Provider(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], test_provider.name)
        self.assertEqual(EXAMPLE['description'], test_provider.description)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'description': 'description',
            },
            test_provider._query_mapping._mapping,
        )


class TestProviderFlavorCapabilities(base.TestCase):
    def test_basic(self):
        test_flav_cap = provider.ProviderFlavorCapabilities()
        self.assertEqual('flavor_capabilities', test_flav_cap.resources_key)
        self.assertEqual(
            '/lbaas/providers/%(provider)s/flavor_capabilities',
            test_flav_cap.base_path,
        )
        self.assertFalse(test_flav_cap.allow_create)
        self.assertFalse(test_flav_cap.allow_fetch)
        self.assertFalse(test_flav_cap.allow_commit)
        self.assertFalse(test_flav_cap.allow_delete)
        self.assertTrue(test_flav_cap.allow_list)

    def test_make_it(self):
        test_flav_cap = provider.ProviderFlavorCapabilities(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], test_flav_cap.name)
        self.assertEqual(EXAMPLE['description'], test_flav_cap.description)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'description': 'description',
            },
            test_flav_cap._query_mapping._mapping,
        )
