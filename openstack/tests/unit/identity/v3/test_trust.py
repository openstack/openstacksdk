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

from openstack.identity.v3 import trust

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'project_id': '1',
    'expires_at': '2016-03-09T12:14:57.233772',
    'id': IDENTIFIER,
    'impersonation': True,
    'trustee_user_id': '2',
    'trustor_user_id': '3',
    'roles': [{'name': 'test-role'}],
    'redelegation_count': '0',
}


class TestTrust(testtools.TestCase):

    def test_basic(self):
        sot = trust.Trust()
        self.assertEqual('trust', sot.resource_key)
        self.assertEqual('trusts', sot.resources_key)
        self.assertEqual('/OS-TRUST/trusts', sot.base_path)
        self.assertEqual('identity', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = trust.Trust(EXAMPLE)
        self.assertEqual(EXAMPLE['project_id'],
                         sot.project_id)
        dt = datetime.datetime(2016, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.expires_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertTrue(sot.is_impersonation)
        self.assertEqual(EXAMPLE['trustee_user_id'], sot.trustee_user_id)
        self.assertEqual(EXAMPLE['trustor_user_id'], sot.trustor_user_id)
        self.assertEqual(EXAMPLE['roles'], sot.roles)
        self.assertEqual(EXAMPLE['redelegation_count'], sot.redelegation_count)
