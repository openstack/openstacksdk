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

from openstack.shared_file_system.v2 import share_snapshot
from openstack.tests.unit import base

IDENTIFIER = '6d221c1d-0200-461e-8d20-24b4776b9ddb'
EXAMPLE = {
    "status": "creating",
    "share_id": "406ea93b-32e9-4907-a117-148b3945749f",
    "user_id": "5c7bdb6eb0504d54a619acf8375c08ce",
    "name": "snapshot_share1",
    "created_at": "2021-06-07T11:50:39.756808",
    "description": "Here is a snapshot of share Share1",
    "share_proto": "NFS",
    "share_size": 1,
    "id": "6d221c1d-0200-461e-8d20-24b4776b9ddb",
    "project_id": "cadd7139bc3148b8973df097c0911016",
    "size": 1,
}


class TestShareSnapshot(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.status_code = 202
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = '3.0'
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_basic(self):
        snapshot_resource = share_snapshot.ShareSnapshot()
        self.assertEqual('snapshots', snapshot_resource.resources_key)
        self.assertEqual('/snapshots', snapshot_resource.base_path)
        self.assertTrue(snapshot_resource.allow_list)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
                "snapshot_id": "snapshot_id",
            },
            snapshot_resource._query_mapping._mapping,
        )

    def test_make_share_snapshot(self):
        snapshot_resource = share_snapshot.ShareSnapshot(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], snapshot_resource.id)
        self.assertEqual(EXAMPLE['share_id'], snapshot_resource.share_id)
        self.assertEqual(EXAMPLE['user_id'], snapshot_resource.user_id)
        self.assertEqual(EXAMPLE['created_at'], snapshot_resource.created_at)
        self.assertEqual(EXAMPLE['status'], snapshot_resource.status)
        self.assertEqual(EXAMPLE['name'], snapshot_resource.name)
        self.assertEqual(EXAMPLE['description'], snapshot_resource.description)
        self.assertEqual(EXAMPLE['share_proto'], snapshot_resource.share_proto)
        self.assertEqual(EXAMPLE['share_size'], snapshot_resource.share_size)
        self.assertEqual(EXAMPLE['project_id'], snapshot_resource.project_id)
        self.assertEqual(EXAMPLE['size'], snapshot_resource.size)

    def test_reset_status(self):
        sot = share_snapshot.ShareSnapshot(**EXAMPLE)
        microversion = sot._get_microversion(self.sess)

        fetch_resp = mock.Mock()
        fetch_resp.body = EXAMPLE
        fetch_resp.body.update({'status': 'error'})

        fetch_resp.status_code = 200
        fetch_resp.headers = {'content-type': 'application/json'}
        fetch_resp.json = mock.Mock(return_value=fetch_resp.body)
        self.sess.get = mock.Mock(return_value=fetch_resp)

        self.assertIsNone(sot.reset_status(self.sess, 'error'))

        url = f'snapshots/{IDENTIFIER}/action'
        body = {"reset_status": {"status": "error"}}
        headers = {'Accept': ''}

        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion=microversion
        )

    def test_force_delete(self):
        sot = share_snapshot.ShareSnapshot(**EXAMPLE)
        microversion = sot._get_microversion(self.sess)

        self.assertIsNone(sot.force_delete(self.sess))

        url = f'snapshots/{IDENTIFIER}/action'
        body = {'force_delete': None}
        headers = {'Accept': ''}

        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion=microversion
        )
