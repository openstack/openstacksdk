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

import testtools

from openstack.compute.v2 import hypervisor

EXAMPLE = {
    'id': 'IDENTIFIER',
    'name': 'hypervisor_hostname',
    'state': 'up',
    'status': 'enabled',
}


class TestHypervisor(testtools.TestCase):

    def test_basic(self):
        sot = hypervisor.Hypervisor()
        self.assertEqual('hypervisor', sot.resource_key)
        self.assertEqual('hypervisors', sot.resources_key)
        self.assertEqual('/os-hypervisors', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = hypervisor.Hypervisor(EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['status'], sot.status)
