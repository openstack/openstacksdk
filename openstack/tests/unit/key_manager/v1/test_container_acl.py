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

from typing import Any

from openstack.key_manager.v1 import container_acl
from openstack.tests.unit import base


CONTAINER_ID = "container-uuid-123"
ACL_REF = f'http://localhost/v1/containers/{CONTAINER_ID}/acl'
EXAMPLE: dict[str, Any] = {
    'acl_ref': ACL_REF,
    'read': {'users': ['user-id-1', 'user-id-2'], 'project-access': False},
    'created': '2015-03-09T12:14:57.233772',
    'updated': '2015-03-09T12:15:57.233772',
}


class TestContainerACL(base.TestCase):
    def test_basic(self):
        sot = container_acl.ContainerACL()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/containers/%(container_id)s/acl', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.requires_id)
        self.assertEqual('PUT', sot.create_opts.method)
        self.assertFalse(sot.create_opts.requires_id)
        self.assertEqual('PATCH', sot.commit_method)

    def test_make_it(self):
        sot = container_acl.ContainerACL(container_id=CONTAINER_ID, **EXAMPLE)
        self.assertEqual(EXAMPLE['acl_ref'], sot.acl_ref)
        self.assertEqual(EXAMPLE['read'], sot.read)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(CONTAINER_ID, sot.container_id)
