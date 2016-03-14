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

from openstack.image.v2 import member

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'created_at': '2015-03-09T12:14:57.233772',
    'image_id': '2',
    'member_id': IDENTIFIER,
    'status': '4',
    'updated_at': '2015-03-09T12:15:57.233772',
}


class TestMember(testtools.TestCase):
    def test_basic(self):
        sot = member.Member()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('members', sot.resources_key)
        self.assertEqual('/images/%(image_id)s/members', sot.base_path)
        self.assertEqual('image', sot.service.service_type)
        self.assertEqual('member_id', sot.id_attribute)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = member.Member(EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        dt = datetime.datetime(2015, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['image_id'], sot.image_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
