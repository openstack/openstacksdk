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

from openstack.network.v2 import port_binding
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'host': 'host1',
    'profile': {},
    'vif_details': {'bridge_name': 'br-int'},
    'vif_type': 'ovs',
    'vnic_type': 'normal',
}


class TestPortBinding(base.TestCase):
    def test_basic(self):
        sot = port_binding.PortBinding()
        self.assertEqual('binding', sot.resource_key)
        self.assertEqual('bindings', sot.resources_key)
        self.assertEqual('/ports/%(port_id)s/bindings', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = port_binding.PortBinding(**EXAMPLE)
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['profile'], sot.profile)
        self.assertEqual(EXAMPLE['vif_details'], sot.vif_details)
        self.assertEqual(EXAMPLE['vif_type'], sot.vif_type)
        self.assertCountEqual(EXAMPLE['vnic_type'], sot.vnic_type)
