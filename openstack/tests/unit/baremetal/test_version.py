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

from openstack.tests.unit import base

from openstack.baremetal import version

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'links': '2',
    'status': '3',
    'updated': '4',
}


class TestVersion(base.TestCase):

    def test_basic(self):
        sot = version.Version()
        self.assertEqual('version', sot.resource_key)
        self.assertEqual('versions', sot.resources_key)
        self.assertEqual('/', sot.base_path)
        self.assertEqual('baremetal', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_head)
        self.assertEqual('PUT', sot.update_method)
        self.assertEqual('POST', sot.create_method)

    def test_make_it(self):
        sot = version.Version(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated)
