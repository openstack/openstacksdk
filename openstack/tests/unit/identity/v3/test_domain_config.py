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

from openstack.identity.v3 import domain_config
from openstack.tests.unit import base


EXAMPLE = {
    'identity': {
        'driver': 'ldap',
    },
    'ldap': {
        'url': 'ldap://myldap.com:389/',
        'user_tree_dn': 'ou=Users,dc=my_new_root,dc=org',
    },
}


class TestDomainConfig(base.TestCase):
    def test_basic(self):
        sot = domain_config.DomainConfig()
        self.assertEqual('config', sot.resource_key)
        self.assertEqual('/domains/%(domain_id)s/config', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

    def test_make_it(self):
        sot = domain_config.DomainConfig(**EXAMPLE)
        self.assertIsInstance(sot.identity, domain_config.DomainConfigDriver)
        self.assertEqual(EXAMPLE['identity']['driver'], sot.identity.driver)
        self.assertIsInstance(sot.ldap, domain_config.DomainConfigLDAP)
        self.assertEqual(EXAMPLE['ldap']['url'], sot.ldap.url)
        self.assertEqual(
            EXAMPLE['ldap']['user_tree_dn'],
            sot.ldap.user_tree_dn,
        )
