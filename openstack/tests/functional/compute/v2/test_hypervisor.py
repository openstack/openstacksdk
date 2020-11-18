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
        super(TestHypervisor, self).setUp()

    def test_list_hypervisors(self):
        rslt = list(self.conn.compute.hypervisors())
        self.assertIsNotNone(rslt)

        rslt = list(self.conn.compute.hypervisors(details=True))
        self.assertIsNotNone(rslt)

    def test_get_find_hypervisors(self):
        for hypervisor in self.conn.compute.hypervisors():
            self.conn.compute.get_hypervisor(hypervisor.id)
            self.conn.compute.find_hypervisor(hypervisor.id)
