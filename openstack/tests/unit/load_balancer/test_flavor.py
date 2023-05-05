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

import uuid

from openstack.load_balancer.v2 import flavor
from openstack.tests.unit import base


IDENTIFIER = uuid.uuid4()
FLAVOR_PROFILE_ID = uuid.uuid4()
EXAMPLE = {
    'id': IDENTIFIER,
    'name': 'strawberry',
    'description': 'tasty',
    'is_enabled': False,
    'flavor_profile_id': FLAVOR_PROFILE_ID,
}


class TestFlavor(base.TestCase):
    def test_basic(self):
        test_flavor = flavor.Flavor()
        self.assertEqual('flavor', test_flavor.resource_key)
        self.assertEqual('flavors', test_flavor.resources_key)
        self.assertEqual('/lbaas/flavors', test_flavor.base_path)
        self.assertTrue(test_flavor.allow_create)
        self.assertTrue(test_flavor.allow_fetch)
        self.assertTrue(test_flavor.allow_commit)
        self.assertTrue(test_flavor.allow_delete)
        self.assertTrue(test_flavor.allow_list)

    def test_make_it(self):
        test_flavor = flavor.Flavor(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], test_flavor.id)
        self.assertEqual(EXAMPLE['name'], test_flavor.name)
        self.assertEqual(EXAMPLE['description'], test_flavor.description)
        self.assertFalse(test_flavor.is_enabled)
        self.assertEqual(
            EXAMPLE['flavor_profile_id'], test_flavor.flavor_profile_id
        )

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'id': 'id',
                'name': 'name',
                'description': 'description',
                'is_enabled': 'enabled',
                'flavor_profile_id': 'flavor_profile_id',
            },
            test_flavor._query_mapping._mapping,
        )
