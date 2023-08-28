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

from openstack.tests.functional import base


class TestService(base.BaseFunctionalTest):
    # listing services is slooowwww
    TIMEOUT_SCALING_FACTOR = 2.0

    def test_list(self):
        sot = list(self.operator_cloud.block_storage.services())
        self.assertIsNotNone(sot)

    def test_disable_enable(self):
        for srv in self.operator_cloud.block_storage.services():
            # only nova-block_storage can be updated
            if srv.name == 'nova-block_storage':
                self.operator_cloud.block_storage.disable_service(srv)
                self.operator_cloud.block_storage.enable_service(srv)
                break

    def test_find(self):
        for srv in self.operator_cloud.block_storage.services():
            self.operator_cloud.block_storage.find_service(
                srv.name,
                host=srv.host,
                ignore_missing=False,
            )
