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

from openstack.tests.functional.shared_file_system import base


class ShareAccessRuleTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        self.SHARE_NAME = self.getUniqueString()
        mys = self.create_share(
            name=self.SHARE_NAME,
            size=2,
            share_type="dhss_false",
            share_protocol='NFS',
            description=None,
        )
        self.user_cloud.shared_file_system.wait_for_status(
            mys,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.assertIsNotNone(mys)
        self.assertIsNotNone(mys.id)
        self.SHARE_ID = mys.id
        self.SHARE = mys
        access_rule = self.user_cloud.share.create_access_rule(
            self.SHARE_ID,
            access_level="rw",
            access_type="ip",
            access_to="0.0.0.0/0",
        )
        self.ACCESS_ID = access_rule.id
        self.RESOURCE_KEY = access_rule.resource_key

    def tearDown(self):
        self.user_cloud.share.delete_access_rule(
            self.ACCESS_ID, self.SHARE_ID, ignore_missing=True
        )
        super().tearDown()

    def test_get_access_rule(self):
        sot = self.user_cloud.shared_file_system.get_access_rule(
            self.ACCESS_ID
        )
        self.assertEqual(self.ACCESS_ID, sot.id)

    def test_list_access_rules(self):
        rules = self.user_cloud.shared_file_system.access_rules(
            self.SHARE, details=True
        )
        self.assertGreater(len(list(rules)), 0)
        for rule in rules:
            for attribute in (
                'id',
                'created_at',
                'updated_at',
                'access_level',
                'access_type',
                'access_to',
                'share_id',
                'access_key',
                'metadata',
            ):
                self.assertTrue(hasattr(rule, attribute))

    def test_create_delete_access_rule_with_locks(self):
        access_rule = self.user_cloud.share.create_access_rule(
            self.SHARE_ID,
            access_level="rw",
            access_type="ip",
            access_to="203.0.113.10",
            lock_deletion=True,
            lock_visibility=True,
        )

        self.user_cloud.share.delete_access_rule(
            access_rule['id'], self.SHARE_ID, unrestrict=True
        )
        self.user_cloud.shared_file_system.wait_for_delete(access_rule)
