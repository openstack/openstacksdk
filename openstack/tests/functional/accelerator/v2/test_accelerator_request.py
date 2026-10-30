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
    one for use by the tests.
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

    def _delete_server(self, server_id):
        self.user_cloud.compute.delete_server(server_id)
        self.user_cloud.compute.wait_for_delete(
            self.user_cloud.compute.get_server(server_id),
            wait=self._wait_for_timeout,
        )

    def _create_accel_flavor(self, dp_name):
        flavor = self.operator_cloud.compute.create_flavor(
            name=self.getUniqueString('accel-'),
            ram=256,
            vcpus=1,
            disk=1,
        )
        self.addCleanup(
            self.operator_cloud.compute.delete_flavor,
            flavor.id,
        )
        self.operator_cloud.compute.create_flavor_extra_specs(
            flavor,
            {'accel:device_profile': dp_name},
        )
        return flavor

    def test_accelerator_request_binding(self):
        """Test ARQ binding through a Nova instance boot.

        The device profile must match Cyborg's fake driver, which
        registers resource class FPGA and trait CUSTOM_FAKE_DEVICE.
        """
        self.require_service('compute')

        dp_name = self.getUniqueString('bind-dp-')
        dp = self.operator_cloud.accelerator.create_device_profile(
            name=dp_name,
            groups=[
                {
                    'resources:FPGA': '1',
                    'trait:CUSTOM_FAKE_DEVICE': 'required',
                }
            ],
        )
        self.addCleanup(
            self.operator_cloud.accelerator.delete_device_profile,
            dp,
        )
        flavor = self._create_accel_flavor(dp_name)

        server = self.user_cloud.compute.create_server(
            name=self.getUniqueString('arq-bind-'),
            flavor_id=flavor.id,
            image_id=self.image.id,
            networks='none',
        )
        self.addCleanup(
            self._delete_server,
            server.id,
        )
        # Use the admin client to get the server so we can access the compute
        # host attribute for asserts.
        server = self.operator_cloud.compute.wait_for_server(
            server,
            wait=self._wait_for_timeout,
        )
        self.assertEqual('ACTIVE', server.status)

        # Find the ARQ bound to this server.
        arqs = list(self.user_cloud.accelerator.accelerator_requests())
        bound = [a for a in arqs if a.instance_uuid == server.id]
        self.assertEqual(1, len(bound))
        arq = bound[0]
        self.assertEqual(server.id, arq.instance_uuid)
        self.assertEqual(server.project_id, arq.project_id)
        self.assertEqual('Bound', arq.state)
        self.assertEqual(server.hypervisor_hostname, arq.hostname)
        self.assertIsNotNone(arq.device_rp_uuid)
        self.assertEqual('TEST_PCI', arq.attach_handle_type)
        self.assertIsNotNone(arq.attach_handle_info)
