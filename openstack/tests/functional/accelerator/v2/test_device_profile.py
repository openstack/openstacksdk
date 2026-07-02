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

from openstack.accelerator.v2 import device_profile as _device_profile
from openstack.tests.functional import base


class TestDeviceProfile(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('accelerator')
        self.NAME = self.getUniqueString()
        self.GROUPS = [
            {
                'resources:CUSTOM_ACCELERATOR_FPGA': '1',
                'trait:CUSTOM_FPGA_INTEL': 'required',
            }
        ]
        self.device_profile = (
            self.operator_cloud.accelerator.create_device_profile(
                name=self.NAME,
                groups=self.GROUPS,
            )
        )
        self.addCleanup(self._delete_device_profile, self.device_profile)

    def _delete_device_profile(self, dp):
        self.operator_cloud.accelerator.delete_device_profile(dp)
        names = [
            d.name for d in self.operator_cloud.accelerator.device_profiles()
        ]
        self.assertNotIn(dp.name, names)

    def test_device_profile(self):
        # Get as regular user
        dp = self.user_cloud.accelerator.get_device_profile(
            self.device_profile.uuid
        )
        self.assertIsInstance(dp, _device_profile.DeviceProfile)
        self.assertEqual(self.NAME, dp.name)

        # List as regular user
        names = [
            dp.name for dp in self.user_cloud.accelerator.device_profiles()
        ]
        self.assertIn(self.NAME, names)

    def test_device_profile_admin(self):
        # Get
        dp = self.operator_cloud.accelerator.get_device_profile(
            self.device_profile.uuid
        )
        self.assertIsInstance(dp, _device_profile.DeviceProfile)
        self.assertEqual(self.NAME, dp.name)

        # List
        names = [
            dp.name for dp in self.operator_cloud.accelerator.device_profiles()
        ]
        self.assertIn(self.NAME, names)

        # Delete (create a separate one to avoid disrupting cleanup)
        name = self.getUniqueString()
        dp = self.operator_cloud.accelerator.create_device_profile(
            name=name,
            groups=self.GROUPS,
        )
        self._delete_device_profile(dp)
