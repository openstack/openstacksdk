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

from openstack.accelerator.v2 import device as _device
from openstack.tests.functional import base


class TestDevice(base.BaseFunctionalTest):
    """Test devices discovered by the fake driver.

    The fake driver creates one device on startup, so listing and
    getting devices should always return results without any test
    setup.
    """

    def setUp(self):
        super().setUp()
        self.require_service('accelerator')

    def test_device(self):
        # List
        devices = list(self.operator_cloud.accelerator.devices())
        self.assertGreater(
            len(devices),
            0,
            'no devices found: is the fake driver enabled?',
        )
        self.assertIsInstance(devices[0], _device.Device)

        # Get
        device = self.operator_cloud.accelerator.get_device(devices[0].uuid)
        self.assertIsInstance(device, _device.Device)
        self.assertEqual(devices[0].uuid, device.uuid)
