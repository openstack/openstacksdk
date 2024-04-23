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

from openstack.network.v2 import local_ip as _local_ip
from openstack.tests.functional import base


class TestLocalIP(base.BaseFunctionalTest):
    LOCAL_IP_ID = None

    def setUp(self):
        super().setUp()

        if not self.user_cloud.network.find_extension("local_ip"):
            self.skipTest("Local IP extension disabled")

        self.LOCAL_IP_NAME = self.getUniqueString()
        self.LOCAL_IP_DESCRIPTION = self.getUniqueString()
        self.LOCAL_IP_NAME_UPDATED = self.getUniqueString()
        self.LOCAL_IP_DESCRIPTION_UPDATED = self.getUniqueString()
        local_ip = self.user_cloud.network.create_local_ip(
            name=self.LOCAL_IP_NAME,
            description=self.LOCAL_IP_DESCRIPTION,
        )
        assert isinstance(local_ip, _local_ip.LocalIP)
        self.assertEqual(self.LOCAL_IP_NAME, local_ip.name)
        self.assertEqual(self.LOCAL_IP_DESCRIPTION, local_ip.description)
        self.LOCAL_IP_ID = local_ip.id

    def tearDown(self):
        sot = self.user_cloud.network.delete_local_ip(self.LOCAL_IP_ID)
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.user_cloud.network.find_local_ip(self.LOCAL_IP_NAME)
        self.assertEqual(self.LOCAL_IP_ID, sot.id)

    def test_get(self):
        sot = self.user_cloud.network.get_local_ip(self.LOCAL_IP_ID)
        self.assertEqual(self.LOCAL_IP_NAME, sot.name)

    def test_list(self):
        names = [
            local_ip.name for local_ip in self.user_cloud.network.local_ips()
        ]
        self.assertIn(self.LOCAL_IP_NAME, names)

    def test_update(self):
        sot = self.user_cloud.network.update_local_ip(
            self.LOCAL_IP_ID,
            name=self.LOCAL_IP_NAME_UPDATED,
            description=self.LOCAL_IP_DESCRIPTION_UPDATED,
        )
        self.assertEqual(self.LOCAL_IP_NAME_UPDATED, sot.name)
        self.assertEqual(self.LOCAL_IP_DESCRIPTION_UPDATED, sot.description)
