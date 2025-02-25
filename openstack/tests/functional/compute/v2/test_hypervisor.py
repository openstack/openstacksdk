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


class TestHypervisor(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

    def test_list_hypervisors(self):
        rslt = list(self.operator_cloud.compute.hypervisors())
        self.assertIsNotNone(rslt)

        rslt = list(self.operator_cloud.compute.hypervisors(details=True))
        self.assertIsNotNone(rslt)

    def test_get_find_hypervisors(self):
        for hypervisor in self.operator_cloud.compute.hypervisors():
            self.operator_cloud.compute.get_hypervisor(hypervisor.id)
            self.operator_cloud.compute.find_hypervisor(hypervisor.id)
