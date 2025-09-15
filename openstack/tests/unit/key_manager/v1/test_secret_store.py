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

from openstack.key_manager.v1 import secret_store
from openstack.tests.unit import base


EXAMPLE = {
    "status": "ACTIVE",
    "updated": "2016-08-22T23:46:45.114283",
    "name": "PKCS11 HSM",
    "created": "2016-08-22T23:46:45.114283",
    "secret_store_ref": "http://localhost:9311/v1/secret-stores/4d27b7a7-b82f-491d-88c0-746bd67dadc8",
    "global_default": True,
    "crypto_plugin": "p11_crypto",
    "secret_store_plugin": "store_crypto",
}


class TestSecretStore(base.TestCase):
    def test_basic(self):
        sot = secret_store.SecretStore()
        self.assertEqual('secret_stores', sot.resources_key)
        self.assertEqual('/secret-stores', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = secret_store.SecretStore(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['secret_store_ref'], sot.secret_store_ref)
        self.assertEqual(EXAMPLE['global_default'], sot.global_default)
        self.assertEqual(EXAMPLE['crypto_plugin'], sot.crypto_plugin)
        self.assertEqual(
            EXAMPLE['secret_store_plugin'], sot.secret_store_plugin
        )
        # Test the alternate_id extraction
        self.assertEqual(
            '4d27b7a7-b82f-491d-88c0-746bd67dadc8', sot.secret_store_id
        )
