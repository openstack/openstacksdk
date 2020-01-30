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

from openstack.network.v2 import port_forwarding

EXAMPLE = {
    'id': 'pf_id',
    'protocol': 'tcp',
    'internal_ip_address': '1.2.3.4',
    'floatingip_id': 'floating-ip-uuid',
    'internal_port': 80,
    'internal_port_id': 'internal-port-uuid',
    'external_port': 8080,
    'description': 'description'
}


class TestFloatingIP(base.TestCase):

    def test_basic(self):
        sot = port_forwarding.PortForwarding()
        self.assertEqual('port_forwarding', sot.resource_key)
        self.assertEqual('port_forwardings', sot.resources_key)
        self.assertEqual(
            '/floatingips/%(floatingip_id)s/port_forwardings',
            sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({'internal_port_id': 'internal_port_id',
                              'external_port': 'external_port',
                              'limit': 'limit',
                              'marker': 'marker',
                              'protocol': 'protocol'},
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = port_forwarding.PortForwarding(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['floatingip_id'], sot.floatingip_id)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['internal_ip_address'],
                         sot.internal_ip_address)
        self.assertEqual(EXAMPLE['internal_port'], sot.internal_port)
        self.assertEqual(EXAMPLE['internal_port_id'], sot.internal_port_id)
        self.assertEqual(EXAMPLE['external_port'], sot.external_port)
        self.assertEqual(EXAMPLE['description'], sot.description)
