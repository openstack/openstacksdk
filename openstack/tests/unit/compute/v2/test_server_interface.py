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

from openstack.tests.unit import base

from openstack.compute.v2 import server_interface

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'fixed_ips': [
        {
            'ip_address': '192.168.1.1',
            'subnet_id': 'f8a6e8f8-c2ec-497c-9f23-da9616de54ef'
        }
    ],
    'mac_addr': '2',
    'net_id': '3',
    'port_id': '4',
    'port_state': '5',
    'server_id': '6',
}


class TestServerInterface(base.TestCase):

    def test_basic(self):
        sot = server_interface.ServerInterface()
        self.assertEqual('interfaceAttachment', sot.resource_key)
        self.assertEqual('interfaceAttachments', sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/os-interface', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = server_interface.ServerInterface(**EXAMPLE)
        self.assertEqual(EXAMPLE['fixed_ips'], sot.fixed_ips)
        self.assertEqual(EXAMPLE['mac_addr'], sot.mac_addr)
        self.assertEqual(EXAMPLE['net_id'], sot.net_id)
        self.assertEqual(EXAMPLE['port_id'], sot.port_id)
        self.assertEqual(EXAMPLE['port_state'], sot.port_state)
        self.assertEqual(EXAMPLE['server_id'], sot.server_id)
