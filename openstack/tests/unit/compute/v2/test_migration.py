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

from openstack.compute.v2 import migration
from openstack.tests.unit import base

EXAMPLE = {
    'uuid': '42341d4b-346a-40d0-83c6-5f4f6892b650',
    'instance_uuid': '9128d044-7b61-403e-b766-7547076ff6c1',
    'user_id': '78348f0e-97ee-4d70-ad34-189692673ea2',
    'project_id': '9842f0f7-1229-4355-afe7-15ebdbb8c3d8',
    'created_at': '2016-06-23T14:42:02.000000',
    'updated_at': '2016-06-23T14:42:02.000000',
    'status': 'migrating',
    'source_compute': 'compute10',
    'source_node': 'node10',
    'dest_host': '5.6.7.8',
    'dest_compute': 'compute20',
    'dest_node': 'node20',
    'migration_type': 'resize',
    'old_instance_type_id': 5,
    'new_instance_type_id': 6,
}


class TestMigration(base.TestCase):
    def test_basic(self):
        sot = migration.Migration()
        self.assertIsNone(sot.resource_key)  # we don't support fetch
        self.assertEqual('migrations', sot.resources_key)
        self.assertEqual('/os-migrations', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'host': 'host',
                'status': 'status',
                'migration_type': 'migration_type',
                'source_compute': 'source_compute',
                'user_id': 'user_id',
                'project_id': 'project_id',
                'changes_since': 'changes-since',
                'changes_before': 'changes-before',
                'server_id': 'instance_uuid',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = migration.Migration(**EXAMPLE)
        self.assertEqual(EXAMPLE['uuid'], sot.id)
        self.assertEqual(EXAMPLE['instance_uuid'], sot.server_id)
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
        self.assertEqual(EXAMPLE['migration_type'], sot.migration_type)
        self.assertEqual(EXAMPLE['old_instance_type_id'], sot.old_flavor_id)
        self.assertEqual(EXAMPLE['new_instance_type_id'], sot.new_flavor_id)
