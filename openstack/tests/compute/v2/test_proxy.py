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

from openstack.compute.v2 import _proxy
from openstack.tests import test_proxy_base


class TestComputeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestComputeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_extension_find(self):
        self.verify_find('openstack.compute.v2.extension.Extension.find',
                         self.proxy.find_extension)

    def test_extension_list(self):
        self.verify_list('openstack.compute.v2.extension.Extension.list',
                         self.proxy.list_extensions)

    def test_flavor_create(self):
        self.verify_create('openstack.compute.v2.flavor.Flavor.create',
                           self.proxy.create_flavor)

    def test_flavor_delete(self):
        self.verify_delete('openstack.compute.v2.flavor.Flavor.delete',
                           self.proxy.delete_flavor)

    def test_flavor_find(self):
        self.verify_find('openstack.compute.v2.flavor.Flavor.find',
                         self.proxy.find_flavor)

    def test_flavor_get(self):
        self.verify_get('openstack.compute.v2.flavor.Flavor.get',
                        self.proxy.get_flavor)

    def test_flavor_list(self):
        self.verify_list('openstack.compute.v2.flavor.Flavor.list',
                         self.proxy.list_flavors)

    def test_flavor_update(self):
        self.verify_update('openstack.compute.v2.flavor.Flavor.update',
                           self.proxy.update_flavor)

    def test_image_create(self):
        self.verify_create('openstack.compute.v2.image.Image.create',
                           self.proxy.create_image)

    def test_image_delete(self):
        self.verify_delete('openstack.compute.v2.image.Image.delete',
                           self.proxy.delete_image)

    def test_image_find(self):
        self.verify_find('openstack.compute.v2.image.Image.find',
                         self.proxy.find_image)

    def test_image_get(self):
        self.verify_get('openstack.compute.v2.image.Image.get',
                        self.proxy.get_image)

    def test_image_list(self):
        self.verify_list('openstack.compute.v2.image.Image.list',
                         self.proxy.list_images)

    def test_image_update(self):
        self.verify_update('openstack.compute.v2.image.Image.update',
                           self.proxy.update_image)

    def test_keypair_create(self):
        self.verify_create('openstack.compute.v2.keypair.Keypair.create',
                           self.proxy.create_keypair)

    def test_keypair_delete(self):
        self.verify_delete('openstack.compute.v2.keypair.Keypair.delete',
                           self.proxy.delete_keypair)

    def test_keypair_find(self):
        self.verify_find('openstack.compute.v2.keypair.Keypair.find',
                         self.proxy.find_keypair)

    def test_keypair_get(self):
        self.verify_get('openstack.compute.v2.keypair.Keypair.get',
                        self.proxy.get_keypair)

    def test_keypair_list(self):
        self.verify_list('openstack.compute.v2.keypair.Keypair.list',
                         self.proxy.list_keypairs)

    def test_keypair_update(self):
        self.verify_update('openstack.compute.v2.keypair.Keypair.update',
                           self.proxy.update_keypair)

    def test_limits_absolute_find(self):
        self.verify_find(
            'openstack.compute.v2.limits_absolute.LimitsAbsolute.find',
            self.proxy.find_limits_absolute)

    def test_limits_absolute_list(self):
        self.verify_list(
            'openstack.compute.v2.limits_absolute.LimitsAbsolute.list',
            self.proxy.list_limits_absolute)

    def test_limits_rate_find(self):
        self.verify_find('openstack.compute.v2.limits_rate.LimitsRate.find',
                         self.proxy.find_limits_rate)

    def test_limits_rate_list(self):
        self.verify_list('openstack.compute.v2.limits_rate.LimitsRate.list',
                         self.proxy.list_limits_rate)

    def test_server_interface_create(self):
        self.verify_create(
            'openstack.compute.v2.server_interface.ServerInterface.create',
            self.proxy.create_server_interface)

    def test_server_interface_delete(self):
        self.verify_delete(
            'openstack.compute.v2.server_interface.ServerInterface.delete',
            self.proxy.delete_server_interface)

    def test_server_interface_find(self):
        self.verify_find(
            'openstack.compute.v2.server_interface.ServerInterface.find',
            self.proxy.find_server_interface)

    def test_server_interface_get(self):
        self.verify_get(
            'openstack.compute.v2.server_interface.ServerInterface.get',
            self.proxy.get_server_interface)

    def test_server_interface_list(self):
        self.verify_list(
            'openstack.compute.v2.server_interface.ServerInterface.list',
            self.proxy.list_server_interfaces)

    def test_server_interface_update(self):
        self.verify_update(
            'openstack.compute.v2.server_interface.ServerInterface.update',
            self.proxy.update_server_interface)

    def test_server_ip_find(self):
        self.verify_find('openstack.compute.v2.server_ip.ServerIP.find',
                         self.proxy.find_server_ip)

    def test_server_ip_list(self):
        self.verify_list('openstack.compute.v2.server_ip.ServerIP.list',
                         self.proxy.list_server_ips)

    def test_server_create(self):
        self.verify_create('openstack.compute.v2.server.Server.create',
                           self.proxy.create_server)

    def test_server_delete(self):
        self.verify_delete('openstack.compute.v2.server.Server.delete',
                           self.proxy.delete_server)

    def test_server_find(self):
        self.verify_find('openstack.compute.v2.server.Server.find',
                         self.proxy.find_server)

    def test_server_get(self):
        self.verify_get('openstack.compute.v2.server.Server.get',
                        self.proxy.get_server)

    def test_server_list(self):
        self.verify_list('openstack.compute.v2.server.Server.list',
                         self.proxy.list_servers)

    def test_server_update(self):
        self.verify_update('openstack.compute.v2.server.Server.update',
                           self.proxy.update_server)
