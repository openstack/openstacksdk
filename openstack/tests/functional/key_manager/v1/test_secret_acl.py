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

from openstack.key_manager.v1 import secret_acl as _secret_acl
from openstack.tests.functional import base


class TestSecretACL(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('key-manager')

        self.secret = self.operator_cloud.key_manager.create_secret(
            name=self.getUniqueString('secret'),
            payload='functional-secret-acl-payload',
            payload_content_type='text/plain',
            secret_type='opaque',
        )
        self.secret_id = self.secret.secret_id
        self.assertIsNotNone(self.secret_id)

        self.addCleanup(
            self.operator_cloud.key_manager.delete_secret,
            self.secret_id,
            ignore_missing=True,
        )
        self.addCleanup(
            self.operator_cloud.key_manager.delete_secret_acl,
            self.secret_id,
            ignore_missing=True,
        )

    def test_secret_acl(self):
        key_manager = self.operator_cloud.key_manager
        user_id = self.operator_cloud.current_user_id

        acl = key_manager.set_secret_acl(
            self.secret_id,
            read={'users': [user_id], 'project-access': False},
        )
        self.assertIsInstance(acl, _secret_acl.SecretACL)
        self.assertIsNotNone(acl.acl_ref)

        acl = key_manager.get_secret_acl(self.secret_id)
        self.assertIsInstance(acl, _secret_acl.SecretACL)
        self.assertFalse(acl.read['project-access'])
        self.assertIn(user_id, acl.read.get('users', []))

        acl = key_manager.update_secret_acl(
            self.secret_id, read={'project-access': True}
        )
        self.assertIsInstance(acl, _secret_acl.SecretACL)
        self.assertIsNotNone(acl.acl_ref)

        acl = key_manager.get_secret_acl(self.secret_id)
        self.assertTrue(acl.read['project-access'])

        self.assertIsNone(key_manager.delete_secret_acl(self.secret_id))

        acl = key_manager.get_secret_acl(self.secret_id)
        self.assertIsInstance(acl, _secret_acl.SecretACL)
        self.assertTrue(acl.read['project-access'])
