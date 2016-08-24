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

import testtools

from openstack.key_manager.v1 import container

ID_VAL = "123"
IDENTIFIER = 'http://localhost/containers/%s' % ID_VAL
EXAMPLE = {
    'container_ref': IDENTIFIER,
    'created': '2015-03-09T12:14:57.233772',
    'name': '3',
    'secret_refs': ['4'],
    'status': '5',
    'type': '6',
    'updated': '2015-03-09T12:15:57.233772',
    'consumers': ['7']
}


class TestContainer(testtools.TestCase):

    def test_basic(self):
        sot = container.Container()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('containers', sot.resources_key)
        self.assertEqual('/containers', sot.base_path)
        self.assertEqual('key-manager', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = container.Container(**EXAMPLE)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['secret_refs'], sot.secret_refs)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['container_ref'], sot.id)
        self.assertEqual(EXAMPLE['container_ref'], sot.container_ref)
        self.assertEqual(ID_VAL, sot.container_id)
        self.assertEqual(EXAMPLE['consumers'], sot.consumers)
