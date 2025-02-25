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

from openstack.tests.functional.block_storage.v3 import base


class TestCapabilities(base.BaseBlockStorageTest):
    # getting capabilities can be slow
    TIMEOUT_SCALING_FACTOR = 1.5

    def test_get(self):
        services = list(self.operator_cloud.block_storage.services())
        host = [
            service
            for service in services
            if service.binary == 'cinder-volume'
        ][0].host

        sot = self.operator_cloud.block_storage.get_capabilities(host)
        self.assertIn('description', sot)
        self.assertIn('display_name', sot)
        self.assertIn('driver_version', sot)
        self.assertIn('namespace', sot)
        self.assertIn('pool_name', sot)
        self.assertIn('properties', sot)
        self.assertIn('replication_targets', sot)
        self.assertIn('storage_protocol', sot)
        self.assertIn('vendor_name', sot)
        self.assertIn('visibility', sot)
        self.assertIn('volume_backend_name', sot)
