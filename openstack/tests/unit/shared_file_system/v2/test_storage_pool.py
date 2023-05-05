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

from openstack.shared_file_system.v2 import storage_pool
from openstack.tests.unit import base


EXAMPLE = {
    "name": "opencloud@alpha#ALPHA_pool",
    "host": "opencloud",
    "backend": "alpha",
    "pool": "ALPHA_pool",
    "capabilities": {
        "pool_name": "ALPHA_pool",
        "total_capacity_gb": 1230.0,
        "free_capacity_gb": 1210.0,
        "reserved_percentage": 0,
        "share_backend_name": "ALPHA",
        "storage_protocol": "NFS_CIFS",
        "vendor_name": "Open Source",
        "driver_version": "1.0",
        "timestamp": "2021-07-31T00:28:02.935569",
        "driver_handles_share_servers": True,
        "snapshot_support": True,
        "create_share_from_snapshot_support": True,
        "revert_to_snapshot_support": True,
        "mount_snapshot_support": True,
        "dedupe": False,
        "compression": False,
        "replication_type": None,
        "replication_domain": None,
        "sg_consistent_snapshot_support": "pool",
        "ipv4_support": True,
        "ipv6_support": False,
    },
}


class TestStoragePool(base.TestCase):
    def test_basic(self):
        pool_resource = storage_pool.StoragePool()
        self.assertEqual('pools', pool_resource.resources_key)
        self.assertEqual('/scheduler-stats/pools', pool_resource.base_path)
        self.assertTrue(pool_resource.allow_list)

        self.assertDictEqual(
            {
                'pool': 'pool',
                'backend': 'backend',
                'host': 'host',
                'limit': 'limit',
                'marker': 'marker',
                'capabilities': 'capabilities',
                'share_type': 'share_type',
            },
            pool_resource._query_mapping._mapping,
        )

    def test_make_storage_pool(self):
        pool_resource = storage_pool.StoragePool(**EXAMPLE)
        self.assertEqual(EXAMPLE['pool'], pool_resource.pool)
        self.assertEqual(EXAMPLE['host'], pool_resource.host)
        self.assertEqual(EXAMPLE['name'], pool_resource.name)
        self.assertEqual(EXAMPLE['backend'], pool_resource.backend)
        self.assertEqual(EXAMPLE['capabilities'], pool_resource.capabilities)
