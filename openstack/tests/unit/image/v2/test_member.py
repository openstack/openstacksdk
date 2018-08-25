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

from openstack.image.v2 import member

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'created_at': '2015-03-09T12:14:57.233772',
    'image_id': '2',
    'member_id': IDENTIFIER,
    'status': '4',
    'updated_at': '2015-03-09T12:15:57.233772',
}


class TestMember(base.TestCase):
    def test_basic(self):
        sot = member.Member()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('members', sot.resources_key)
        self.assertEqual('/images/%(image_id)s/members', sot.base_path)
        self.assertEqual('member', sot._alternate_id())
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = member.Member(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['image_id'], sot.image_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
