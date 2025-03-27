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

from unittest import mock

from keystoneauth1 import adapter

from openstack.block_storage.v3 import group_snapshot
from openstack.tests.unit import base

GROUP_SNAPSHOT = {
    "id": "6f519a48-3183-46cf-a32f-41815f813986",
    "group_id": "6f519a48-3183-46cf-a32f-41815f814444",
    "status": "available",
    "created_at": "2015-09-16T09:28:52.000000",
    "name": "my_group_snapshot1",
    "description": "my first group snapshot",
    "group_type_id": "7270c56e-6354-4528-8e8b-f54dee2232c8",
    "project_id": "7ccf4863071f44aeb8f141f65780c51b",
}


class TestGroupSnapshot(base.TestCase):
    def test_basic(self):
        resource = group_snapshot.GroupSnapshot()
        self.assertEqual("group_snapshot", resource.resource_key)
        self.assertEqual("group_snapshots", resource.resources_key)
        self.assertEqual("/group_snapshots", resource.base_path)
        self.assertTrue(resource.allow_create)
        self.assertTrue(resource.allow_fetch)
        self.assertTrue(resource.allow_delete)
        self.assertTrue(resource.allow_list)
        self.assertFalse(resource.allow_commit)

    def test_make_resource(self):
        resource = group_snapshot.GroupSnapshot(**GROUP_SNAPSHOT)
        self.assertEqual(GROUP_SNAPSHOT["created_at"], resource.created_at)
        self.assertEqual(GROUP_SNAPSHOT["description"], resource.description)
        self.assertEqual(GROUP_SNAPSHOT["group_id"], resource.group_id)
        self.assertEqual(
            GROUP_SNAPSHOT["group_type_id"], resource.group_type_id
        )
        self.assertEqual(GROUP_SNAPSHOT["id"], resource.id)
        self.assertEqual(GROUP_SNAPSHOT["name"], resource.name)
        self.assertEqual(GROUP_SNAPSHOT["project_id"], resource.project_id)
        self.assertEqual(GROUP_SNAPSHOT["status"], resource.status)


class TestGroupSnapshotActions(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.headers = {}
        self.resp.status_code = 202

        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.get = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = '3.0'

    def test_reset_status(self):
        resource = group_snapshot.GroupSnapshot(**GROUP_SNAPSHOT)

        self.assertIsNotNone(resource.reset_status(self.sess, 'new_status'))

        url = f'group_snapshots/{GROUP_SNAPSHOT["id"]}/action'
        body = {'reset_status': {'status': 'new_status'}}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers={'Accept': ''},
            microversion='3.0',
        )
