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

from openstack.identity.v3 import trust

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'allow_redelegation': False,
    'expires_at': '2016-03-09T12:14:57.233772',
    'id': IDENTIFIER,
    'impersonation': True,
    'links': {'self': 'fake_link'},
    'project_id': '1',
    'redelegated_trust_id': None,
    'redelegation_count': '0',
    'remaining_uses': 10,
    'role_links': {'self': 'other_fake_link'},
    'trustee_user_id': '2',
    'trustor_user_id': '3',
    'roles': [{'name': 'test-role'}],
}


class TestTrust(base.TestCase):

    def test_basic(self):
        sot = trust.Trust()
        self.assertEqual('trust', sot.resource_key)
        self.assertEqual('trusts', sot.resources_key)
        self.assertEqual('/OS-TRUST/trusts', sot.base_path)
        self.assertEqual('identity', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = trust.Trust(**EXAMPLE)
        self.assertEqual(EXAMPLE['allow_redelegation'], sot.allow_redelegation)
        self.assertEqual(EXAMPLE['expires_at'], sot.expires_at)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertTrue(sot.is_impersonation)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['role_links'], sot.role_links)
        self.assertEqual(EXAMPLE['redelegated_trust_id'],
                         sot.redelegated_trust_id)
        self.assertEqual(EXAMPLE['remaining_uses'], sot.remaining_uses)
        self.assertEqual(EXAMPLE['trustee_user_id'], sot.trustee_user_id)
        self.assertEqual(EXAMPLE['trustor_user_id'], sot.trustor_user_id)
        self.assertEqual(EXAMPLE['roles'], sot.roles)
        self.assertEqual(EXAMPLE['redelegation_count'], sot.redelegation_count)
