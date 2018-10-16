# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_floating_ip_common
----------------------------------

Tests floating IP resource methods for Neutron and Nova-network.
"""

from mock import patch

from openstack.cloud import meta
from openstack.cloud import openstackcloud
from openstack.tests import fakes
from openstack.tests.unit import base


class TestFloatingIP(base.TestCase):

    @patch.object(openstackcloud._OpenStackCloudMixin, 'get_floating_ip')
    @patch.object(openstackcloud._OpenStackCloudMixin, '_attach_ip_to_server')
    @patch.object(openstackcloud._OpenStackCloudMixin, 'available_floating_ip')
    def test_add_auto_ip(
            self, mock_available_floating_ip, mock_attach_ip_to_server,
            mock_get_floating_ip):
        server_dict = fakes.make_fake_server(
            server_id='server-id', name='test-server', status="ACTIVE",
            addresses={}
        )
        floating_ip_dict = {
            "id": "this-is-a-floating-ip-id",
            "fixed_ip_address": None,
            "internal_network": None,
            "floating_ip_address": "203.0.113.29",
            "network": "this-is-a-net-or-pool-id",
            "attached": False,
            "status": "ACTIVE"
        }

        mock_available_floating_ip.return_value = floating_ip_dict

        self.cloud.add_auto_ip(server=server_dict)

        mock_attach_ip_to_server.assert_called_with(
            timeout=60, wait=False, server=server_dict,
            floating_ip=floating_ip_dict, skip_attach=False)

    @patch.object(openstackcloud._OpenStackCloudMixin, '_add_ip_from_pool')
    def test_add_ips_to_server_pool(self, mock_add_ip_from_pool):
        server_dict = fakes.make_fake_server(
            server_id='romeo', name='test-server', status="ACTIVE",
            addresses={})
        pool = 'nova'

        self.cloud.add_ips_to_server(server_dict, ip_pool=pool)

        mock_add_ip_from_pool.assert_called_with(
            server_dict, pool, reuse=True, wait=False, timeout=60,
            fixed_address=None, nat_destination=None)

    @patch.object(openstackcloud._OpenStackCloudMixin, 'has_service')
    @patch.object(openstackcloud._OpenStackCloudMixin, 'get_floating_ip')
    @patch.object(openstackcloud._OpenStackCloudMixin, '_add_auto_ip')
    def test_add_ips_to_server_ipv6_only(
            self, mock_add_auto_ip,
            mock_get_floating_ip,
            mock_has_service):
        self.cloud._floating_ip_source = None
        self.cloud.force_ipv4 = False
        self.cloud._local_ipv6 = True
        mock_has_service.return_value = False
        server = fakes.make_fake_server(
            server_id='server-id', name='test-server', status="ACTIVE",
            addresses={
                'private': [{
                    'addr': "10.223.160.141",
                    'version': 4
                }],
                'public': [{
                    u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:ae:7d:42',
                    u'OS-EXT-IPS:type': u'fixed',
                    'addr': "2001:4800:7819:103:be76:4eff:fe05:8525",
                    'version': 6
                }]
            }
        )
        server_dict = meta.add_server_interfaces(self.cloud, server)

        new_server = self.cloud.add_ips_to_server(server=server_dict)
        mock_get_floating_ip.assert_not_called()
        mock_add_auto_ip.assert_not_called()
        self.assertEqual(
            new_server['interface_ip'],
            '2001:4800:7819:103:be76:4eff:fe05:8525')
        self.assertEqual(new_server['private_v4'], '10.223.160.141')
        self.assertEqual(new_server['public_v4'], '')
        self.assertEqual(
            new_server['public_v6'], '2001:4800:7819:103:be76:4eff:fe05:8525')

    @patch.object(openstackcloud._OpenStackCloudMixin, 'has_service')
    @patch.object(openstackcloud._OpenStackCloudMixin, 'get_floating_ip')
    @patch.object(openstackcloud._OpenStackCloudMixin, '_add_auto_ip')
    def test_add_ips_to_server_rackspace(
            self, mock_add_auto_ip,
            mock_get_floating_ip,
            mock_has_service):
        self.cloud._floating_ip_source = None
        self.cloud.force_ipv4 = False
        self.cloud._local_ipv6 = True
        mock_has_service.return_value = False
        server = fakes.make_fake_server(
            server_id='server-id', name='test-server', status="ACTIVE",
            addresses={
                'private': [{
                    'addr': "10.223.160.141",
                    'version': 4
                }],
                'public': [{
                    'addr': "104.130.246.91",
                    'version': 4
                }, {
                    'addr': "2001:4800:7819:103:be76:4eff:fe05:8525",
                    'version': 6
                }]
            }
        )
        server_dict = meta.add_server_interfaces(self.cloud, server)

        new_server = self.cloud.add_ips_to_server(server=server_dict)
        mock_get_floating_ip.assert_not_called()
        mock_add_auto_ip.assert_not_called()
        self.assertEqual(
            new_server['interface_ip'],
            '2001:4800:7819:103:be76:4eff:fe05:8525')

    @patch.object(openstackcloud._OpenStackCloudMixin, 'has_service')
    @patch.object(openstackcloud._OpenStackCloudMixin, 'get_floating_ip')
    @patch.object(openstackcloud._OpenStackCloudMixin, '_add_auto_ip')
    def test_add_ips_to_server_rackspace_local_ipv4(
            self, mock_add_auto_ip,
            mock_get_floating_ip,
            mock_has_service):
        self.cloud._floating_ip_source = None
        self.cloud.force_ipv4 = False
        self.cloud._local_ipv6 = False
        mock_has_service.return_value = False
        server = fakes.make_fake_server(
            server_id='server-id', name='test-server', status="ACTIVE",
            addresses={
                'private': [{
                    'addr': "10.223.160.141",
                    'version': 4
                }],
                'public': [{
                    'addr': "104.130.246.91",
                    'version': 4
                }, {
                    'addr': "2001:4800:7819:103:be76:4eff:fe05:8525",
                    'version': 6
                }]
            }
        )
        server_dict = meta.add_server_interfaces(self.cloud, server)

        new_server = self.cloud.add_ips_to_server(server=server_dict)
        mock_get_floating_ip.assert_not_called()
        mock_add_auto_ip.assert_not_called()
        self.assertEqual(new_server['interface_ip'], '104.130.246.91')

    @patch.object(openstackcloud._OpenStackCloudMixin, 'add_ip_list')
    def test_add_ips_to_server_ip_list(self, mock_add_ip_list):
        server_dict = fakes.make_fake_server(
            server_id='server-id', name='test-server', status="ACTIVE",
            addresses={})
        ips = ['203.0.113.29', '172.24.4.229']

        self.cloud.add_ips_to_server(server_dict, ips=ips)

        mock_add_ip_list.assert_called_with(
            server_dict, ips, wait=False, timeout=60, fixed_address=None)

    @patch.object(openstackcloud._OpenStackCloudMixin, '_needs_floating_ip')
    @patch.object(openstackcloud._OpenStackCloudMixin, '_add_auto_ip')
    def test_add_ips_to_server_auto_ip(
            self, mock_add_auto_ip, mock_needs_floating_ip):
        server_dict = fakes.make_fake_server(
            server_id='server-id', name='test-server', status="ACTIVE",
            addresses={})

        # TODO(mordred) REMOVE THIS MOCK WHEN THE NEXT PATCH LANDS
        # SERIOUSLY THIS TIME. NEXT PATCH - WHICH SHOULD ADD MOCKS FOR
        # list_ports AND list_networks AND list_subnets. BUT THAT WOULD
        # BE NOT ACTUALLY RELATED TO THIS PATCH. SO DO IT NEXT PATCH
        mock_needs_floating_ip.return_value = True

        self.cloud.add_ips_to_server(server_dict)

        mock_add_auto_ip.assert_called_with(
            server_dict, wait=False, timeout=60, reuse=True)
