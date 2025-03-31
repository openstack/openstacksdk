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

from openstack.tests.functional import base


class TestAccount(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('object-store')

    def tearDown(self):
        account = self.operator_cloud.object_store.get_account_metadata()
        self.operator_cloud.object_store.delete_account_metadata(
            account.metadata.keys()
        )
        super().tearDown()

    def test_system_metadata(self):
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertGreaterEqual(account.account_bytes_used, 0)
        self.assertGreaterEqual(account.account_container_count, 0)
        self.assertGreaterEqual(account.account_object_count, 0)

    def test_custom_metadata(self):
        # get custom metadata
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertFalse(account.metadata)

        # set no custom metadata
        self.operator_cloud.object_store.set_account_metadata()
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertFalse(account.metadata)

        # set empty custom metadata
        self.operator_cloud.object_store.set_account_metadata(k0='')
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertFalse(account.metadata)

        # set custom metadata
        self.operator_cloud.object_store.set_account_metadata(k1='v1')
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertTrue(account.metadata)
        self.assertEqual(1, len(account.metadata))
        self.assertIn('k1', account.metadata)
        self.assertEqual('v1', account.metadata['k1'])

        # set more custom metadata
        self.operator_cloud.object_store.set_account_metadata(k2='v2')
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertTrue(account.metadata)
        self.assertEqual(2, len(account.metadata))
        self.assertIn('k1', account.metadata)
        self.assertEqual('v1', account.metadata['k1'])
        self.assertIn('k2', account.metadata)
        self.assertEqual('v2', account.metadata['k2'])

        # update custom metadata
        self.operator_cloud.object_store.set_account_metadata(k1='v1.1')
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertTrue(account.metadata)
        self.assertEqual(2, len(account.metadata))
        self.assertIn('k1', account.metadata)
        self.assertEqual('v1.1', account.metadata['k1'])
        self.assertIn('k2', account.metadata)
        self.assertEqual('v2', account.metadata['k2'])

        # unset custom metadata
        self.operator_cloud.object_store.delete_account_metadata(['k1'])
        account = self.operator_cloud.object_store.get_account_metadata()
        self.assertTrue(account.metadata)
        self.assertEqual(1, len(account.metadata))
        self.assertIn('k2', account.metadata)
        self.assertEqual('v2', account.metadata['k2'])
