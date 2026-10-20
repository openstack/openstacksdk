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

from openstack.key_manager.v1 import secret_store as _secret_store
from openstack.tests.functional import base


class TestSecretStore(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('key-manager')

    def test_secret_store(self):
        """Test Secret Store operations"""
        key_manager = self.operator_cloud.key_manager

        # Test list secret stores
        secret_stores = list(key_manager.secret_stores())
        self.assertIsInstance(secret_stores, list)

        for store in secret_stores:
            self.assertIsInstance(store, _secret_store.SecretStore)
            self.assertIsNotNone(store.name)
            self.assertIsNotNone(store.status)
            self.assertIsNotNone(store.secret_store_id)
            # secret_store_id is derived from secret_store_ref via
            # HREFToUUID. .id on a *list* result is the raw href (it is
            # only rewritten to the UUID for the global-default / preferred
            # singletons below, via _normalize_secret_store_resource), so
            # compare against the href, not against .secret_store_id.
            self.assertEqual(store.id, store.secret_store_ref)
            self.assertIn(store.secret_store_id, store.secret_store_ref)

        # Test list secret stores with filters
        global_default_stores = list(
            key_manager.secret_stores(global_default=True)
        )
        self.assertIsInstance(global_default_stores, list)

        active_stores = list(key_manager.secret_stores(status="ACTIVE"))
        self.assertIsInstance(active_stores, list)

        # Test get global default secret store
        if global_default_stores:
            default_store = key_manager.get_global_default_secret_store()
            self.assertIsInstance(default_store, _secret_store.SecretStore)
            self.assertIsNotNone(default_store.name)
            self.assertTrue(default_store.global_default)
            self.assertIsNotNone(default_store.secret_store_id)
            self.assertEqual(default_store.secret_store_id, default_store.id)
            self.assertIn(
                default_store.secret_store_id,
                default_store.secret_store_ref,
            )

        # Test get preferred secret store
        if secret_stores:
            preferred_store = key_manager.get_preferred_secret_store()
            self.assertIsInstance(preferred_store, _secret_store.SecretStore)
            self.assertIsNotNone(preferred_store.name)
            self.assertIsNotNone(preferred_store.secret_store_id)
            self.assertEqual(
                preferred_store.secret_store_id, preferred_store.id
            )
            self.assertIn(
                preferred_store.secret_store_id,
                preferred_store.secret_store_ref,
            )
