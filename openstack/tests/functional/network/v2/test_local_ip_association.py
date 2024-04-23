#   Copyright 2021 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from openstack.network.v2 import local_ip_association as _local_ip_association
from openstack.tests.functional import base


class TestLocalIPAssociation(base.BaseFunctionalTest):
    LOCAL_IP_ID = None
    FIXED_PORT_ID = None
    FIXED_IP = None

    def setUp(self):
        super().setUp()

        if not self.user_cloud.network.find_extension("local_ip"):
            self.skipTest("Local IP extension disabled")

        self.LOCAL_IP_ID = self.getUniqueString()
        self.FIXED_PORT_ID = self.getUniqueString()
        self.FIXED_IP = self.getUniqueString()
        local_ip_association = (
            self.user_cloud.network.create_local_ip_association(
                local_ip=self.LOCAL_IP_ID,
                fixed_port_id=self.FIXED_PORT_ID,
                fixed_ip=self.FIXED_IP,
            )
        )
        assert isinstance(
            local_ip_association, _local_ip_association.LocalIPAssociation
        )
        self.assertEqual(self.LOCAL_IP_ID, local_ip_association.local_ip_id)
        self.assertEqual(
            self.FIXED_PORT_ID, local_ip_association.fixed_port_id
        )
        self.assertEqual(self.FIXED_IP, local_ip_association.fixed_ip)

    def tearDown(self):
        sot = self.user_cloud.network.delete_local_ip_association(
            self.LOCAL_IP_ID, self.FIXED_PORT_ID
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_local_ip_association(
            self.FIXED_PORT_ID, self.LOCAL_IP_ID
        )
        self.assertEqual(self.FIXED_PORT_ID, sot.fixed_port_id)

    def test_get(self):
        sot = self.user_cloud.network.get_local_ip_association(
            self.FIXED_PORT_ID, self.LOCAL_IP_ID
        )
        self.assertEqual(self.FIXED_PORT_ID, sot.fixed_port_id)

    def test_list(self):
        fixed_port_id = [
            obj.fixed_port_id
            for obj in self.user_cloud.network.local_ip_associations(
                self.LOCAL_IP_ID
            )
        ]
        self.assertIn(self.FIXED_PORT_ID, fixed_port_id)
