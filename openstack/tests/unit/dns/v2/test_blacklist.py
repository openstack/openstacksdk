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

from openstack.dns.v2 import blacklist
from openstack.tests.unit import base

IDENTIFIER = '373cb85e-0f4a-487a-846e-dce7a65cca4d'
EXAMPLE = {
    'id': IDENTIFIER,
    'description': 'blacklist test description',
    'pattern': '.*example.com.',
}


class TestBlackList(base.TestCase):
    def test_basic(self):
        sot = blacklist.Blacklist()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('blacklists', sot.resources_key)
        self.assertEqual('/blacklists', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertEqual('PATCH', sot.commit_method)

    def test_make_it(self):
        sot = blacklist.Blacklist(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['pattern'], sot.pattern)
