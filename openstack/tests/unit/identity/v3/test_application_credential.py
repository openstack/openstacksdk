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

from openstack.identity.v3 import application_credential
from openstack.tests.unit import base


EXAMPLE = {
    "user": {"id": "8ac43bb0926245cead88676a96c750d3"},
    "name": 'monitoring',
    "secret": 'rEaqvJka48mpv',
    "roles": [{"name": "Reader"}],
    "access_rules": [
        {"path": "/v2.0/metrics", "service": "monitoring", "method": "GET"},
    ],
    "expires_at": '2018-02-27T18:30:59Z',
    "description": "Application credential for monitoring",
    "unrestricted": "False",
    "project_id": "3",
    "links": {"self": "http://example.com/v3/application_credential_1"},
}


class TestApplicationCredential(base.TestCase):
    def test_basic(self):
        sot = application_credential.ApplicationCredential()
        self.assertEqual('application_credential', sot.resource_key)
        self.assertEqual('application_credentials', sot.resources_key)
        self.assertEqual(
            '/users/%(user_id)s/application_credentials', sot.base_path
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = application_credential.ApplicationCredential(**EXAMPLE)
        self.assertEqual(EXAMPLE['user'], sot.user)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['secret'], sot.secret)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['expires_at'], sot.expires_at)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['roles'], sot.roles)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['access_rules'], sot.access_rules)
