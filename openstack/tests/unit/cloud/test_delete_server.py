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

"""
test_delete_server
----------------------------------

Tests for the `delete_server` command.
"""
import uuid

from openstack.cloud import exc as shade_exc
from openstack.tests import fakes
from openstack.tests.unit import base


class TestDeleteServer(base.TestCase):

    def test_delete_server(self):
        """
        Test that server delete is called when wait=False
        """
        server = fakes.make_fake_server('1234', 'daffy', 'ACTIVE')
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
        ])
        self.assertTrue(self.cloud.delete_server('daffy', wait=False))

        self.assert_calls()

    def test_delete_server_already_gone(self):
        """
        Test that we return immediately when server is already gone
        """
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertFalse(self.cloud.delete_server('tweety', wait=False))

        self.assert_calls()

    def test_delete_server_already_gone_wait(self):
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertFalse(self.cloud.delete_server('speedy', wait=True))
        self.assert_calls()

    def test_delete_server_wait_for_deleted(self):
        """
        Test that delete_server waits for the server to be gone
        """
        server = fakes.make_fake_server('9999', 'wily', 'ACTIVE')
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '9999'])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertTrue(self.cloud.delete_server('wily', wait=True))

        self.assert_calls()

    def test_delete_server_fails(self):
        """
        Test that delete_server raises non-404 exceptions
        """
        server = fakes.make_fake_server('1212', 'speedy', 'ACTIVE')
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1212']),
                 status_code=400),
        ])

        self.assertRaises(
            shade_exc.OpenStackCloudException,
            self.cloud.delete_server, 'speedy',
            wait=False)

        self.assert_calls()

    def test_delete_server_no_cinder(self):
        """
        Test that deleting server works when cinder is not available
        """
        orig_has_service = self.cloud.has_service

        def fake_has_service(service_type):
            if service_type == 'volume':
                return False
            return orig_has_service(service_type)
        self.cloud.has_service = fake_has_service

        server = fakes.make_fake_server('1234', 'porky', 'ACTIVE')
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
        ])
        self.assertTrue(self.cloud.delete_server('porky', wait=False))

        self.assert_calls()

    def test_delete_server_delete_ips(self):
        """
        Test that deleting server and fips works
        """
        server = fakes.make_fake_server('1234', 'porky', 'ACTIVE')
        fip_id = uuid.uuid4().hex

        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json'],
                     qs_elements=['floating_ip_address=172.24.5.5']),
                 complete_qs=True,
                 json={'floatingips': [{
                     'router_id': 'd23abc8d-2991-4a55-ba98-2aaea84cc72f',
                     'tenant_id': '4969c491a3c74ee4af974e6d800c62de',
                     'floating_network_id': '376da547-b977-4cfe-9cba7',
                     'fixed_ip_address': '10.0.0.4',
                     'floating_ip_address': '172.24.5.5',
                     'port_id': 'ce705c24-c1ef-408a-bda3-7bbd946164ac',
                     'id': fip_id,
                     'status': 'ACTIVE'}]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'floatingips',
                             '{fip_id}.json'.format(fip_id=fip_id)])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json']),
                 complete_qs=True,
                 json={'floatingips': []}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertTrue(self.cloud.delete_server(
            'porky', wait=True, delete_ips=True))

        self.assert_calls()

    def test_delete_server_delete_ips_bad_neutron(self):
        """
        Test that deleting server with a borked neutron doesn't bork
        """
        server = fakes.make_fake_server('1234', 'porky', 'ACTIVE')

        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'floatingips.json'],
                     qs_elements=['floating_ip_address=172.24.5.5']),
                 complete_qs=True,
                 status_code=404),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertTrue(self.cloud.delete_server(
            'porky', wait=True, delete_ips=True))

        self.assert_calls()

    def test_delete_server_delete_fips_nova(self):
        """
        Test that deleting server with a borked neutron doesn't bork
        """
        self.cloud._floating_ip_source = 'nova'
        server = fakes.make_fake_server('1234', 'porky', 'ACTIVE')

        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-floating-ips']),
                 json={'floating_ips': [
                     {
                         'fixed_ip': None,
                         'id': 1,
                         'instance_id': None,
                         'ip': '172.24.5.5',
                         'pool': 'nova'
                     }]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-floating-ips', '1'])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-floating-ips']),
                 json={'floating_ips': []}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertTrue(self.cloud.delete_server(
            'porky', wait=True, delete_ips=True))

        self.assert_calls()
