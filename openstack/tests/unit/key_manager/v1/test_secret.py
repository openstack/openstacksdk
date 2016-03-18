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

import datetime

import testtools

from openstack.key_manager.v1 import secret

IDENTIFIER = 'http://localhost:9311/v1/secrets/ID'
EXAMPLE = {
    'algorithm': '1',
    'bit_length': '2',
    'content_types': '3',
    'expiration': '2017-03-09T12:14:57.233772',
    'mode': '5',
    'name': '6',
    'secret_ref': IDENTIFIER,
    'status': '8',
    'updated': '2015-03-09T12:15:57.233772',
}


class TestSecret(testtools.TestCase):

    def test_basic(self):
        sot = secret.Secret()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('secrets', sot.resources_key)
        self.assertEqual('/secrets', sot.base_path)
        self.assertEqual('key-manager', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = secret.Secret(EXAMPLE)
        self.assertEqual(EXAMPLE['algorithm'], sot.algorithm)
        self.assertEqual(EXAMPLE['bit_length'], sot.bit_length)
        self.assertEqual(EXAMPLE['content_types'], sot.content_types)
        dt = datetime.datetime(2017, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.expires_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['mode'], sot.mode)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['secret_ref'], sot.secret_ref)
        self.assertEqual(EXAMPLE['status'], sot.status)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['secret_ref'], sot.id)
