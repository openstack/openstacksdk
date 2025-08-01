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

from openstack.compute.v2 import hypervisor as _hypervisor
from openstack.tests.functional import base


class TestHypervisor(base.BaseFunctionalTest):
    def test_hypervisors(self):
        hypervisors = list(self.operator_cloud.compute.hypervisors())
        self.assertIsNotNone(hypervisors)

        hypervisors = list(
            self.operator_cloud.compute.hypervisors(details=True)
        )
        self.assertIsNotNone(hypervisors)

        hypervisor = self.operator_cloud.compute.get_hypervisor(
            hypervisors[0].id
        )
        self.assertIsInstance(hypervisor, _hypervisor.Hypervisor)
        self.assertEqual(hypervisor.id, hypervisors[0].id)

        hypervisor = self.operator_cloud.compute.find_hypervisor(
            hypervisors[0].name, ignore_missing=False
        )
        self.assertIsInstance(hypervisor, _hypervisor.Hypervisor)
        self.assertEqual(hypervisor.id, hypervisors[0].id)
