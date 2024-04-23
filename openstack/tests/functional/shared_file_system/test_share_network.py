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

from openstack.shared_file_system.v2 import share_network as _share_network
from openstack.tests.functional.shared_file_system import base


class ShareNetworkTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        self.NETWORK_NAME = self.getUniqueString()
        net = self.user_cloud.network.create_network(name=self.NETWORK_NAME)
        self.assertIsNotNone(net)
        self.assertIsNotNone(net.id)
        self.NETWORK_ID = net.id

        self.SUBNET_NAME = self.getUniqueString()
        subnet = self.user_cloud.network.create_subnet(
            name=self.SUBNET_NAME,
            network_id=self.NETWORK_ID,
            ip_version=4,
            cidr='10.0.0.0/24',
        )
        self.SUBNET_ID = subnet.id

        self.SHARE_NETWORK_NAME = self.getUniqueString()
        snt = self.user_cloud.shared_file_system.create_share_network(
            name=self.SHARE_NETWORK_NAME,
            neutron_net_id=self.NETWORK_ID,
            neutron_subnet_id=self.SUBNET_ID,
        )

        self.assertIsNotNone(snt)
        self.assertIsNotNone(snt.id)
        self.SHARE_NETWORK_ID = snt.id

    def tearDown(self):
        sot = self.user_cloud.shared_file_system.delete_share_network(
            self.SHARE_NETWORK_ID, ignore_missing=True
        )
        self.assertIsNone(sot)
        self.user_cloud.network.delete_network(self.NETWORK_ID)
        super().tearDown()

    def test_get(self):
        sot = self.user_cloud.shared_file_system.get_share_network(
            self.SHARE_NETWORK_ID
        )
        assert isinstance(sot, _share_network.ShareNetwork)
        self.assertEqual(self.SHARE_NETWORK_ID, sot.id)
        self.assertIsNotNone(sot.share_network_subnets)
        self.assertEqual(
            self.NETWORK_ID,
            sot.share_network_subnets[0]['neutron_net_id'],
        )
        self.assertEqual(
            self.SUBNET_ID,
            sot.share_network_subnets[0]['neutron_subnet_id'],
        )

    def test_list_share_network(self):
        share_nets = self.user_cloud.shared_file_system.share_networks(
            details=False
        )
        self.assertGreater(len(list(share_nets)), 0)
        for share_net in share_nets:
            for attribute in ('id', 'name', 'created_at', 'updated_at'):
                self.assertTrue(hasattr(share_net, attribute))

    def test_delete_share_network(self):
        sot = self.user_cloud.shared_file_system.delete_share_network(
            self.SHARE_NETWORK_ID
        )
        self.assertIsNone(sot)

    def test_update(self):
        unt = self.user_cloud.shared_file_system.update_share_network(
            self.SHARE_NETWORK_ID, description='updated share network'
        )
        get_unt = self.user_cloud.shared_file_system.get_share_network(unt.id)
        self.assertEqual('updated share network', get_unt.description)
