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

from openstack.shared_file_system.v2 import share_group_snapshot
from openstack.tests.unit import base

IDENTIFIER = '38152b6d-e1b5-465f-91bc-20bca4676a2a'
EXAMPLE = {
    "id": IDENTIFIER,
    "name": "snapshot_1",
    "created_at": "2021-10-24T19:36:49.555325",
    "status": "available",
    "description": "first snapshot of sg-1",
    "project_id": "7343d2f7770b4eb6a7bc33f44dcee1e0",
    "share_group_id": "fb41512f-7c49-4304-afb1-66573c7feb14",
}


class TestShareGroupSnapshot(base.TestCase):
    def test_basic(self):
        share_group_snapshots = share_group_snapshot.ShareGroupSnapshot()
        self.assertEqual(
            'share_group_snapshot', share_group_snapshots.resource_key
        )
        self.assertEqual(
            'share_group_snapshots', share_group_snapshots.resources_key
        )
        self.assertEqual(
            '/share-group-snapshots', share_group_snapshots.base_path
        )
        self.assertTrue(share_group_snapshots.allow_create)
        self.assertTrue(share_group_snapshots.allow_fetch)
        self.assertTrue(share_group_snapshots.allow_commit)
        self.assertTrue(share_group_snapshots.allow_delete)
        self.assertTrue(share_group_snapshots.allow_list)
        self.assertFalse(share_group_snapshots.allow_head)

    def test_make_share_groups(self):
        share_group_snapshots = share_group_snapshot.ShareGroupSnapshot(
            **EXAMPLE
        )
        self.assertEqual(EXAMPLE['id'], share_group_snapshots.id)
        self.assertEqual(EXAMPLE['name'], share_group_snapshots.name)
        self.assertEqual(
            EXAMPLE['created_at'], share_group_snapshots.created_at
        )
        self.assertEqual(EXAMPLE['status'], share_group_snapshots.status)
        self.assertEqual(
            EXAMPLE['description'], share_group_snapshots.description
        )
        self.assertEqual(
            EXAMPLE['project_id'], share_group_snapshots.project_id
        )
        self.assertEqual(
            EXAMPLE['share_group_id'], share_group_snapshots.share_group_id
        )


class TestShareGroupSnapshotActions(TestShareGroupSnapshot):
    def setUp(self):
        super(TestShareGroupSnapshot, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = '3.0'
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_reset_status(self):
        sot = share_group_snapshot.ShareGroupSnapshot(**EXAMPLE)
        self.assertIsNone(sot.reset_status(self.sess, 'available'))
        url = f'share-group-snapshots/{IDENTIFIER}/action'
        body = {"reset_status": {"status": 'available'}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_get_members(self):
        sot = share_group_snapshot.ShareGroupSnapshot(**EXAMPLE)
        sot.get_members(self.sess)
        url = f'share-group-snapshots/{IDENTIFIER}/members'
        headers = {'Accept': ''}
        self.sess.get.assert_called_with(
            url,
            headers=headers,
            microversion=self.sess.default_microversion,
        )
