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


from openstack.block_storage.v2 import stats as _stats
from openstack.tests.functional.block_storage.v2 import base


class TestStats(base.BaseBlockStorageTest):

    def setUp(self):
        super(TestStats, self).setUp()

        sot = self.operator_cloud.block_storage.backend_pools()
        for pool in sot:
            self.assertIsInstance(pool, _stats.Pools)

    def test_list(self):
        capList = ['volume_backend_name', 'storage_protocol',
                   'free_capacity_gb', 'driver_version',
                   'goodness_function', 'QoS_support',
                   'vendor_name', 'pool_name', 'thin_provisioning_support',
                   'thick_provisioning_support', 'timestamp',
                   'max_over_subscription_ratio', 'total_volumes',
                   'total_capacity_gb', 'filter_function',
                   'multiattach', 'provisioned_capacity_gb',
                   'allocated_capacity_gb', 'reserved_percentage',
                   'location_info']
        capList.sort()
        pools = self.operator_cloud.block_storage.backend_pools()
        for pool in pools:
            caps = pool.capabilities
            keys = list(caps.keys())
            assert isinstance(caps, dict)
            # Check that we have at minimum listed capabilities
            for cap in sorted(capList):
                self.assertIn(cap, keys)
