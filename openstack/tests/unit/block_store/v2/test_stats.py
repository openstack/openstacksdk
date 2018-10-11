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

from openstack.tests.unit import base

from openstack.block_storage.v2 import stats

POOLS = {"name": "pool1",
         "capabilities": {
             "updated": "2014-10-28T00=00=00-00=00",
             "total_capacity": 1024,
             "free_capacity": 100,
             "volume_backend_name": "pool1",
             "reserved_percentage": "0",
             "driver_version": "1.0.0",
             "storage_protocol": "iSCSI",
             "QoS_support": "false"
         }
         }


class TestBackendPools(base.TestCase):

    def setUp(self):
        super(TestBackendPools, self).setUp()

    def test_basic(self):
        sot = stats.Pools(POOLS)
        self.assertEqual("pool", sot.resource_key)
        self.assertEqual("pools", sot.resources_key)
        self.assertEqual("/scheduler-stats/get_pools?detail=True",
                         sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_commit)
