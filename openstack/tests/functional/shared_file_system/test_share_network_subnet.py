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

from openstack.shared_file_system.v2 import (
    share_network_subnet as _share_network_subnet,
)
from openstack.tests.functional.shared_file_system import base


class ShareNetworkSubnetTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        zones = self.user_cloud.shared_file_system.availability_zones()
        first_zone = next(zones)

        self.SHARE_NETWORK_NAME = self.getUniqueString()
        snt = self.user_cloud.shared_file_system.create_share_network(
            name=self.SHARE_NETWORK_NAME
        )
        self.assertIsNotNone(snt)
        self.assertIsNotNone(snt.id)
        self.SHARE_NETWORK_ID = snt.id
        snsb = self.user_cloud.shared_file_system.create_share_network_subnet(
            self.SHARE_NETWORK_ID, availability_zone=first_zone.name
        )
        self.assertIsNotNone(snsb)
        self.assertIsNotNone(snsb.id)
        self.SHARE_NETWORK_SUBNET_ID = snsb.id

    def tearDown(self):
        subnet = self.user_cloud.shared_file_system.get_share_network_subnet(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID
        )
        fdel = self.user_cloud.shared_file_system.delete_share_network_subnet(
            self.SHARE_NETWORK_ID,
            self.SHARE_NETWORK_SUBNET_ID,
            ignore_missing=True,
        )
        self.assertIsNone(fdel)
        self.user_cloud.shared_file_system.wait_for_delete(subnet)
        sot = self.user_cloud.shared_file_system.delete_share_network(
            self.SHARE_NETWORK_ID, ignore_missing=True
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_get(self):
        sub = self.user_cloud.shared_file_system.get_share_network_subnet(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID
        )
        assert isinstance(sub, _share_network_subnet.ShareNetworkSubnet)

    def test_list(self):
        subs = self.user_cloud.shared_file_system.share_network_subnets(
            self.SHARE_NETWORK_ID
        )
        self.assertGreater(len(list(subs)), 0)
        for sub in subs:
            for attribute in (
                'id',
                'name',
                'created_at',
                'updated_at',
                'share_network_id',
                'availability_zone',
                'cidr',
                'gateway',
                'ip_version',
                'mtu',
                'network_type',
                'neutron_net_id',
                'neutron_subnet_id',
                'segmentation_id',
                'share_network_name',
            ):
                self.assertTrue(hasattr(sub, attribute))
