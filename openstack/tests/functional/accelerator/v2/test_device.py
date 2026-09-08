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
from openstack import utils


class TestDevice(base.BaseFunctionalTest):
    """Test devices discovered by the fake driver.

    The fake driver creates one device on startup, so listing and
    getting devices should always return results without any test
    setup.
    """

    def setUp(self):
        super().setUp()
        self.require_service('accelerator', min_microversion='2.3')
        self._set_operator_cloud(accelerator_default_microversion='2.3')

    def _wait_for_device_status(self, device_id, expected_status):
        for _ in utils.iterate_timeout(
            30,
            (
                f'Timeout waiting for device {device_id} '
                f'to become {expected_status}'
            ),
        ):
            device = self.operator_cloud.accelerator.get_device(device_id)
            if device.status == expected_status:
                return device

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
        self.assertIsNotNone(device.status)

        # Disable
        self.addCleanup(
            self.operator_cloud.accelerator.enable_device,
            device.id,
        )
        self.operator_cloud.accelerator.disable_device(device.id)
        disabled = self._wait_for_device_status(device.id, 'maintaining')
        self.assertEqual('maintaining', disabled.status)

        # Enable
        self.operator_cloud.accelerator.enable_device(device.id)
        enabled = self._wait_for_device_status(device.id, 'enabled')
        self.assertEqual('enabled', enabled.status)
