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

from openstack.compute.v2 import server_migration
from openstack.tests.unit import base

EXAMPLE = {
    'id': 4,
    'server_id': '4cfba335-03d8-49b2-8c52-e69043d1e8fe',
    'server_uuid': '4cfba335-03d8-49b2-8c52-e69043d1e8fe',
    'user_id': '8dbaa0f0-ab95-4ffe-8cb4-9c89d2ac9d24',
    'project_id': '5f705771-3aa9-4f4c-8660-0d9522ffdbea',
    'created_at': '2016-01-29T13:42:02.000000',
    'updated_at': '2016-01-29T13:42:02.000000',
    'status': 'migrating',
    'source_compute': 'compute1',
    'source_node': 'node1',
    'dest_host': '1.2.3.4',
    'dest_compute': 'compute2',
    'dest_node': 'node2',
    'memory_processed_bytes': 12345,
    'memory_remaining_bytes': 111111,
    'memory_total_bytes': 123456,
    'disk_processed_bytes': 23456,
    'disk_remaining_bytes': 211111,
    'disk_total_bytes': 234567,
}


class TestServerMigration(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.sess = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = server_migration.ServerMigration()
        self.assertEqual('migration', sot.resource_key)
        self.assertEqual('migrations', sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/migrations', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

    def test_make_it(self):
        sot = server_migration.ServerMigration(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        # FIXME(stephenfin): This conflicts since there is a server ID in the
        # URI *and* in the body. We need a field that handles both or we need
        # to use different names.
        # self.assertEqual(EXAMPLE['server_uuid'], sot.server_id)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['source_compute'], sot.source_compute)
        self.assertEqual(EXAMPLE['source_node'], sot.source_node)
        self.assertEqual(EXAMPLE['dest_host'], sot.dest_host)
        self.assertEqual(EXAMPLE['dest_compute'], sot.dest_compute)
        self.assertEqual(EXAMPLE['dest_node'], sot.dest_node)
        self.assertEqual(
            EXAMPLE['memory_processed_bytes'],
            sot.memory_processed_bytes,
        )
        self.assertEqual(
            EXAMPLE['memory_remaining_bytes'],
            sot.memory_remaining_bytes,
        )
        self.assertEqual(EXAMPLE['memory_total_bytes'], sot.memory_total_bytes)
        self.assertEqual(
            EXAMPLE['disk_processed_bytes'],
            sot.disk_processed_bytes,
        )
        self.assertEqual(
            EXAMPLE['disk_remaining_bytes'],
            sot.disk_remaining_bytes,
        )
        self.assertEqual(EXAMPLE['disk_total_bytes'], sot.disk_total_bytes)

    @mock.patch.object(
        server_migration.ServerMigration,
        '_get_session',
        lambda self, x: x,
    )
    def test_force_complete(self):
        sot = server_migration.ServerMigration(**EXAMPLE)

        self.assertIsNone(sot.force_complete(self.sess))

        url = 'servers/{}/migrations/{}/action'.format(
            EXAMPLE['server_id'],
            EXAMPLE['id'],
        )
        body = {'force_complete': None}
        self.sess.post.assert_called_with(
            url,
            microversion=mock.ANY,
            json=body,
        )
