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

from openstack.key_manager.v1 import container_acl as _container_acl
from openstack.tests.functional import base


class TestContainerACL(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('key-manager')

        self.container = self.operator_cloud.key_manager.create_container(
            name=self.getUniqueString('container'),
            type='generic',
        )
        self.assertIsNotNone(self.container.container_id)

        # Cleanups run LIFO, so register the container delete first and the
        # ACL reset second; the ACL is reset while the container still exists.
        self.addCleanup(
            self.operator_cloud.key_manager.delete_container,
            self.container,
            ignore_missing=True,
        )
        self.addCleanup(
            self.operator_cloud.key_manager.delete_container_acl,
            self.container,
            ignore_missing=True,
        )

    def test_container_acl(self):
        key_manager = self.operator_cloud.key_manager
        user_id = self.operator_cloud.current_user_id

        acl = key_manager.create_container_acl(
            self.container,
            read={'users': [user_id], 'project-access': False},
        )
        self.assertIsInstance(acl, _container_acl.ContainerACL)
        self.assertIsNotNone(acl.acl_ref)

        acl = key_manager.get_container_acl(self.container)
        self.assertIsInstance(acl, _container_acl.ContainerACL)
        self.assertFalse(acl.read['project-access'])
        self.assertIn(user_id, acl.read.get('users', []))

        acl = key_manager.update_container_acl(
            self.container, read={'project-access': True}
        )
        self.assertIsInstance(acl, _container_acl.ContainerACL)
        self.assertIsNotNone(acl.acl_ref)

        acl = key_manager.get_container_acl(self.container)
        self.assertTrue(acl.read['project-access'])

        self.assertIsNone(key_manager.delete_container_acl(self.container))

        acl = key_manager.get_container_acl(self.container)
        self.assertIsInstance(acl, _container_acl.ContainerACL)
        self.assertTrue(acl.read['project-access'])
