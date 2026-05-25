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

"""
test_keypairs
----------------------------------

Functional tests for keypairs methods
"""

from openstack.tests.functional import base

FAKE_PUBLIC_KEY = (
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCkF3MX59OrlBs3dH5CU7lNmvpbrgZxSpyGj"
    "lnE8Flkirnc/Up22lpjznoxqeoTAwTW034k7Dz6aYIrZGmQwe2TkE084yqvlj45Dkyoj95fW/"
    "sZacm0cZNuL69EObEGHdprfGJQajrpz22NQoCD8TFB8Wv+8om9NH9Le6s+WPe98WC77KLw8qg"
    "fQsbIey+JawPWl4O67ZdL5xrypuRjfIPWjgy/VH85IXg/Z/GONZ2nxHgSShMkwqSFECAC5L3P"
    "HB+0+/12M/iikdatFSVGjpuHvkLOs3oe7m6HlOfluSJ85BzLWBbvva93qkGmLg4ZAc8rPh2O+"
    "YIsBUHNLLMM/oQp Generated-by-Nova\n"
)


class TestKeypairs(base.BaseFunctionalTest):
    def test_create_and_delete(self):
        '''Test creating and deleting keypairs functionality'''
        name = self.getUniqueString('keypair')
        self.addCleanup(self.user_cloud.delete_keypair, name)
        keypair = self.user_cloud.create_keypair(name=name)
        self.assertEqual(keypair['name'], name)
        self.assertIsNotNone(keypair['public_key'])
        self.assertIsNotNone(keypair['private_key'])
        self.assertIsNotNone(keypair['fingerprint'])
        self.assertEqual(keypair['type'], 'ssh')

        keypairs = self.user_cloud.list_keypairs()
        self.assertIn(name, [k['name'] for k in keypairs])

        self.user_cloud.delete_keypair(name)

        keypairs = self.user_cloud.list_keypairs()
        self.assertNotIn(name, [k['name'] for k in keypairs])

    def test_create_and_delete_with_key(self):
        '''Test creating and deleting keypairs functionality'''
        name = self.getUniqueString('keypair')
        self.addCleanup(self.user_cloud.delete_keypair, name)
        keypair = self.user_cloud.create_keypair(
            name=name, public_key=FAKE_PUBLIC_KEY
        )
        self.assertEqual(keypair['name'], name)
        self.assertIsNotNone(keypair['public_key'])
        self.assertIsNone(keypair['private_key'])
        self.assertIsNotNone(keypair['fingerprint'])
        self.assertEqual(keypair['type'], 'ssh')

        keypairs = self.user_cloud.list_keypairs()
        self.assertIn(name, [k['name'] for k in keypairs])

        self.user_cloud.delete_keypair(name)

        keypairs = self.user_cloud.list_keypairs()
        self.assertNotIn(name, [k['name'] for k in keypairs])
