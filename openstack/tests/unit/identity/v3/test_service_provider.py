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

from openstack.identity.v3 import service_provider
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'description': 'An example description',
    'is_enabled': True,
    'auth_url': (
        "https://auth.example.com/v3/OS-FEDERATION/"
        "identity_providers/idp/protocols/saml2/auth"
    ),
    'sp_url': 'https://auth.example.com/Shibboleth.sso/SAML2/ECP',
}


class TestServiceProvider(base.TestCase):
    def test_basic(self):
        sot = service_provider.ServiceProvider()
        self.assertEqual('service_provider', sot.resource_key)
        self.assertEqual('service_providers', sot.resources_key)
        self.assertEqual('/OS-FEDERATION/service_providers', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.create_exclude_id_from_body)
        self.assertEqual('PATCH', sot.commit_method)
        self.assertEqual('PUT', sot.create_method)

        self.assertDictEqual(
            {
                'id': 'id',
                'limit': 'limit',
                'marker': 'marker',
                'is_enabled': 'enabled',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = service_provider.ServiceProvider(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['id'], sot.name)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['is_enabled'], sot.is_enabled)
        self.assertEqual(EXAMPLE['auth_url'], sot.auth_url)
        self.assertEqual(EXAMPLE['sp_url'], sot.sp_url)
