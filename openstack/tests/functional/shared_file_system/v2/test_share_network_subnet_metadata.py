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

from openstack.tests.functional.shared_file_system.v2 import base


class ShareNetworkSubnetMetadataTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        zones = self.operator_cloud.shared_file_system.availability_zones()
        first_zone = next(zones)
        self.user_client = self.user_cloud.shared_file_system

        share_network_name = self.getUniqueString()
        snt = self.user_client.create_share_network(name=share_network_name)
        self.assertIsNotNone(snt)
        self.SHARE_NETWORK_ID = snt.id

        snsb = self.user_client.create_share_network_subnet(
            self.SHARE_NETWORK_ID, availability_zone=first_zone.name
        )
        self.assertIsNotNone(snsb)
        self.SHARE_NETWORK_SUBNET_ID = snsb.id

    def tearDown(self):
        subnet = self.user_client.get_share_network_subnet(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID
        )
        self.user_client.delete_share_network_subnet(
            self.SHARE_NETWORK_ID,
            self.SHARE_NETWORK_SUBNET_ID,
            ignore_missing=True,
        )
        self.user_client.wait_for_delete(subnet)

        self.user_client.delete_share_network(
            self.SHARE_NETWORK_ID, ignore_missing=True
        )

        super().tearDown()

    def test_share_network_subnet_metadata(self):
        # create
        sot = self.user_client.set_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID,
            self.SHARE_NETWORK_SUBNET_ID,
            foo="bar",
        )
        self.assertEqual(sot['metadata'], {"foo": "bar"})

        # get all metadata
        sot = self.user_client.fetch_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID
        )
        self.assertEqual('bar', sot["metadata"]["foo"])

        # get metadata item
        sot = self.user_client.fetch_share_network_subnet_metadata_item(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID, "foo"
        )
        self.assertEqual('bar', sot["metadata"]["foo"])

        # update (merge)
        self.user_client.set_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID,
            self.SHARE_NETWORK_SUBNET_ID,
            new_foo="new_bar",
        )
        sot = self.user_client.fetch_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID
        )
        self.assertEqual(sot['metadata'], {"foo": "bar", "new_foo": "new_bar"})

        # delete
        self.user_client.delete_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID,
            self.SHARE_NETWORK_SUBNET_ID,
            ["foo"],
        )
        sot = self.user_client.fetch_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID
        )
        self.assertEqual(sot['metadata'], {"new_foo": "new_bar"})

        # replace with empty
        sot = self.user_client.set_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID,
            self.SHARE_NETWORK_SUBNET_ID,
            replace=True,
        )
        self.assertEqual(sot['metadata'], {})

        sot = self.user_client.fetch_share_network_subnet_metadata(
            self.SHARE_NETWORK_ID, self.SHARE_NETWORK_SUBNET_ID
        )
        self.assertEqual(sot['metadata'], {})
