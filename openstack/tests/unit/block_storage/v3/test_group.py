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

import copy
from unittest import mock

from keystoneauth1 import adapter

from openstack.block_storage.v3 import group
from openstack.tests.unit import base

GROUP_ID = "6f519a48-3183-46cf-a32f-41815f813986"

GROUP = {
    "id": GROUP_ID,
    "status": "available",
    "availability_zone": "az1",
    "created_at": "2015-09-16T09:28:52.000000",
    "name": "first_group",
    "description": "my first group",
    "group_type": "29514915-5208-46ab-9ece-1cc4688ad0c1",
    "volume_types": ["c4daaf47-c530-4901-b28e-f5f0a359c4e6"],
    "volumes": ["a2cdf1ad-5497-4e57-bd7d-f573768f3d03"],
    "group_snapshot_id": None,
    "source_group_id": None,
    "project_id": "7ccf4863071f44aeb8f141f65780c51b",
}


class TestGroup(base.TestCase):
    def test_basic(self):
        resource = group.Group()
        self.assertEqual("group", resource.resource_key)
        self.assertEqual("groups", resource.resources_key)
        self.assertEqual("/groups", resource.base_path)
        self.assertTrue(resource.allow_create)
        self.assertTrue(resource.allow_fetch)
        self.assertTrue(resource.allow_delete)
        self.assertTrue(resource.allow_commit)
        self.assertTrue(resource.allow_list)

    def test_make_resource(self):
        resource = group.Group(**GROUP)
        self.assertEqual(GROUP["id"], resource.id)
        self.assertEqual(GROUP["status"], resource.status)
        self.assertEqual(
            GROUP["availability_zone"], resource.availability_zone
        )
        self.assertEqual(GROUP["created_at"], resource.created_at)
        self.assertEqual(GROUP["name"], resource.name)
        self.assertEqual(GROUP["description"], resource.description)
        self.assertEqual(GROUP["group_type"], resource.group_type)
        self.assertEqual(GROUP["volume_types"], resource.volume_types)
        self.assertEqual(GROUP["volumes"], resource.volumes)
        self.assertEqual(
            GROUP["group_snapshot_id"], resource.group_snapshot_id
        )
        self.assertEqual(GROUP["source_group_id"], resource.source_group_id)
        self.assertEqual(GROUP["project_id"], resource.project_id)


class TestGroupAction(base.TestCase):
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
        self.sess.default_microversion = '3.38'

    def test_delete(self):
        sot = group.Group(**GROUP)

        self.assertIsNone(sot.delete(self.sess))

        url = f'groups/{GROUP_ID}/action'
        body = {'delete': {'delete-volumes': False}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion
        )

    def test_reset_status(self):
        sot = group.Group(**GROUP)

        self.assertIsNone(sot.reset_status(self.sess, 'new_status'))

        url = f'groups/{GROUP_ID}/action'
        body = {'reset_status': {'status': 'new_status'}}
        self.sess.post.assert_called_with(
            url,
            json=body,
            microversion=sot._max_microversion,
        )

    def test_create_from_source(self):
        resp = mock.Mock()
        resp.body = {'group': copy.deepcopy(GROUP)}
        resp.json = mock.Mock(return_value=resp.body)
        resp.headers = {}
        resp.status_code = 202

        self.sess.post = mock.Mock(return_value=resp)

        sot = group.Group.create_from_source(
            self.sess,
            group_snapshot_id='9a591346-e595-4bc1-94e7-08f264406b63',
            source_group_id='6c5259f6-42ed-4e41-8ffe-e1c667ae9dff',
            name='group_from_source',
            description='a group from source',
        )
        self.assertIsNotNone(sot)

        url = 'groups/action'
        body = {
            'create-from-src': {
                'name': 'group_from_source',
                'description': 'a group from source',
                'group_snapshot_id': '9a591346-e595-4bc1-94e7-08f264406b63',
                'source_group_id': '6c5259f6-42ed-4e41-8ffe-e1c667ae9dff',
            },
        }
        self.sess.post.assert_called_with(
            url,
            json=body,
            microversion=sot._max_microversion,
        )
