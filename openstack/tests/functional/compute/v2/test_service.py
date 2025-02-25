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
    def test_list(self):
        sot = list(self.operator_cloud.compute.services())
        self.assertIsNotNone(sot)

    def test_disable_enable(self):
        self.skipTest("Test is breaking tests that follow")
        for srv in self.operator_cloud.compute.services():
            # only nova-compute can be updated
            if srv.name == 'nova-compute':
                self.operator_cloud.compute.disable_service(srv)
                self.operator_cloud.compute.enable_service(srv)

    def test_update(self):
        self.skipTest("Test is breaking tests that follow")
        for srv in self.operator_cloud.compute.services():
            if srv.name == 'nova-compute':
                self.operator_cloud.compute.update_service_forced_down(
                    srv, None, None, True
                )
                self.operator_cloud.compute.update_service_forced_down(
                    srv, srv.host, srv.binary, False
                )
                self.operator_cloud.compute.update_service(
                    srv, status='enabled'
                )

    def test_find(self):
        for srv in self.operator_cloud.compute.services():
            if srv.name != 'nova-conductor':
                # In devstack there are 2 nova-conductor instances on same host
                self.operator_cloud.compute.find_service(
                    srv.name, host=srv.host, ignore_missing=False
                )
