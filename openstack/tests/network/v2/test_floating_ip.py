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

import mock
import testtools

from openstack.network.v2 import floating_ip

IDENTIFIER = '10.0.0.1'
EXAMPLE = {
    'fixed_ip_address': '1',
    'floating_ip_address': IDENTIFIER,
    'floating_network_id': '3',
    'port_id': '5',
    'tenant_id': '6',
    'router_id': '7',
}


class TestFloatingIP(testtools.TestCase):

    def test_basic(self):
        sot = floating_ip.FloatingIP()
        self.assertEqual('floatingip', sot.resource_key)
        self.assertEqual('floatingips', sot.resources_key)
        self.assertEqual('/floatingips', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = floating_ip.FloatingIP(EXAMPLE)
        self.assertEqual(EXAMPLE['fixed_ip_address'], sot.fixed_ip_address)
        self.assertEqual(EXAMPLE['floating_ip_address'],
                         sot.floating_ip_address)
        self.assertEqual(EXAMPLE['floating_network_id'],
                         sot.floating_network_id)
        self.assertEqual(EXAMPLE['floating_ip_address'], sot.id)
        self.assertEqual(EXAMPLE['port_id'], sot.port_id)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['router_id'], sot.router_id)

    def test_find_available(self):
        mock_session = mock.Mock()
        mock_get = mock.Mock()
        mock_session.get = mock_get
        data = {'floating_ip_address': '10.0.0.1'}
        fake_response = mock.Mock()
        fake_response.body = {floating_ip.FloatingIP.resources_key: [data]}
        mock_get.return_value = fake_response

        result = floating_ip.FloatingIP.find_available(mock_session)

        self.assertEqual('10.0.0.1', result.id)
        p = {'fields': 'floating_ip_address', 'port_id': ''}
        mock_get.assert_called_with(floating_ip.FloatingIP.base_path,
                                    params=p,
                                    service=floating_ip.FloatingIP.service)

    def test_find_available_nada(self):
        mock_session = mock.Mock()
        mock_get = mock.Mock()
        mock_session.get = mock_get
        fake_response = mock.Mock()
        fake_response.body = {floating_ip.FloatingIP.resources_key: []}
        mock_get.return_value = fake_response

        self.assertEqual(None,
                         floating_ip.FloatingIP.find_available(mock_session))
