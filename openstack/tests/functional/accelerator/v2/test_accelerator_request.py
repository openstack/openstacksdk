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

from openstack.accelerator.v2 import accelerator_request as _arq
from openstack.tests.functional import base


class TestAcceleratorRequest(base.BaseFunctionalTest):
    """Test accelerator requests (ARQs).

    ARQ creation requires a device profile to exist. The setUp creates
    one for use by the tests. ARQ binding is not tested here because it
    requires a Nova instance with an accelerator-aware flavor.
    """

    def setUp(self):
        super().setUp()
        self.require_service('accelerator')
        self.DP_NAME = self.getUniqueString()
        self.GROUPS = [
            {
                'resources:CUSTOM_ACCELERATOR_FPGA': '1',
                'trait:CUSTOM_FPGA_INTEL': 'required',
            }
        ]
        self.device_profile = (
            self.operator_cloud.accelerator.create_device_profile(
                name=self.DP_NAME,
                groups=self.GROUPS,
            )
        )
        self.addCleanup(
            self.operator_cloud.accelerator.delete_device_profile,
            self.device_profile,
        )

    def test_accelerator_request(self):
        # Create as regular user (project member)
        arq = self.user_cloud.accelerator.create_accelerator_request(
            device_profile_name=self.DP_NAME,
        )
        self.assertIsInstance(arq, _arq.AcceleratorRequest)
        self.assertIsNotNone(arq.uuid)

        # Get as regular user
        got = self.user_cloud.accelerator.get_accelerator_request(arq.uuid)
        self.assertIsInstance(got, _arq.AcceleratorRequest)
        self.assertEqual(arq.uuid, got.uuid)

        # List as regular user
        arqs = list(self.user_cloud.accelerator.accelerator_requests())
        uuids = [a.uuid for a in arqs]
        self.assertIn(arq.uuid, uuids)

        # Delete as regular user
        self.user_cloud.accelerator.delete_accelerator_request(arq)

        # Verify deletion
        arqs = list(self.user_cloud.accelerator.accelerator_requests())
        uuids = [a.uuid for a in arqs]
        self.assertNotIn(arq.uuid, uuids)

    def test_accelerator_request_admin(self):
        arq = self.operator_cloud.accelerator.create_accelerator_request(
            device_profile_name=self.DP_NAME,
        )
        self.assertIsInstance(arq, _arq.AcceleratorRequest)
        self.operator_cloud.accelerator.delete_accelerator_request(arq)
