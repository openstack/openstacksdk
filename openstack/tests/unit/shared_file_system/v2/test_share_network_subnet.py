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

from openstack.shared_file_system.v2 import share_network_subnet as SNS
from openstack.tests.unit import base

IDENTIFIER = '9cd5a59f-4d22-496f-8b1a-ea4860c24d39'
EXAMPLE = {
    "id": IDENTIFIER,
    "availability_zone": None,
    "share_network_id": "652ef887-b805-4328-b65a-b88c64cb69ec",
    "share_network_name": None,
    "created_at": "2021-02-24T02:45:59.000000",
    "segmentation_id": None,
    "neutron_subnet_id": None,
    "updated_at": None,
    "neutron_net_id": None,
    "ip_version": None,
    "cidr": None,
    "network_type": None,
    "mtu": None,
    "gateway": None,
}


class TestShareNetworkSubnet(base.TestCase):
    def test_basic(self):
        SNS_resource = SNS.ShareNetworkSubnet()
        self.assertEqual('share_network_subnets', SNS_resource.resources_key)
        self.assertEqual(
            '/share-networks/%(share_network_id)s/subnets',
            SNS_resource.base_path,
        )
        self.assertTrue(SNS_resource.allow_list)

    def test_make_share_network_subnet(self):
        SNS_resource = SNS.ShareNetworkSubnet(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], SNS_resource.id)
        self.assertEqual(
            EXAMPLE['availability_zone'], SNS_resource.availability_zone
        )
        self.assertEqual(
            EXAMPLE['share_network_id'], SNS_resource.share_network_id
        )
        self.assertEqual(
            EXAMPLE['share_network_name'], SNS_resource.share_network_name
        )
        self.assertEqual(EXAMPLE['created_at'], SNS_resource.created_at)
        self.assertEqual(
            EXAMPLE['segmentation_id'], SNS_resource.segmentation_id
        )
        self.assertEqual(
            EXAMPLE['neutron_subnet_id'], SNS_resource.neutron_subnet_id
        )
        self.assertEqual(EXAMPLE['updated_at'], SNS_resource.updated_at)
        self.assertEqual(
            EXAMPLE['neutron_net_id'], SNS_resource.neutron_net_id
        )
        self.assertEqual(EXAMPLE['ip_version'], SNS_resource.ip_version)
        self.assertEqual(EXAMPLE['cidr'], SNS_resource.cidr)
        self.assertEqual(EXAMPLE['network_type'], SNS_resource.network_type)
        self.assertEqual(EXAMPLE['mtu'], SNS_resource.mtu)
        self.assertEqual(EXAMPLE['gateway'], SNS_resource.gateway)
