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

from openstack.dns.v2 import tsigkey
from openstack.tests.unit import base

IDENTIFIER = '4c72c7d3-6cfa-4fe1-9984-7705119f0228'
EXAMPLE = {
    "id": IDENTIFIER,
    "name": 'test-key',
    "algorithm": 'hmac-sha512',
    "secret": 'test-secret',
    "scope": 'POOL',
    "resource_id": IDENTIFIER,
}


class TestTsigKey(base.TestCase):
    def test_basic(self):
        sot = tsigkey.TSIGKey()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('tsigkeys', sot.resources_key)
        self.assertEqual('/tsigkeys', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

        self.assertDictEqual(
            {
                'name': 'name',
                'algorithm': 'algorithm',
                'scope': 'scope',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = tsigkey.TSIGKey(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['algorithm'], sot.algorithm)
        self.assertEqual(EXAMPLE['scope'], sot.scope)
        self.assertEqual(EXAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(EXAMPLE['secret'], sot.secret)
