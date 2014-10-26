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

from openstack.network.v2 import _proxy
from openstack.tests import test_proxy_base


class TestNetworkProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestNetworkProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_ip(self):
        self.verify_create('openstack.network.v2.floatingip.FloatingIP.create',
                           self.proxy.create_ip)
        self.verify_delete('openstack.network.v2.floatingip.FloatingIP.delete',
                           self.proxy.delete_ip)
        self.verify_find('openstack.network.v2.floatingip.FloatingIP.find',
                         self.proxy.find_ip)
        self.verify_get('openstack.network.v2.floatingip.FloatingIP.get',
                        self.proxy.get_ip)
        self.verify_list('openstack.network.v2.floatingip.FloatingIP.list',
                         self.proxy.list_ips)
        self.verify_update('openstack.network.v2.floatingip.FloatingIP.update',
                           self.proxy.update_ip)

    def test_network(self):
        self.verify_create('openstack.network.v2.network.Network.create',
                           self.proxy.create_network)
        self.verify_delete('openstack.network.v2.network.Network.delete',
                           self.proxy.delete_network)
        self.verify_find('openstack.network.v2.network.Network.find',
                         self.proxy.find_network)
        self.verify_get('openstack.network.v2.network.Network.get',
                        self.proxy.get_network)
        self.verify_list('openstack.network.v2.network.Network.list',
                         self.proxy.list_networks)
        self.verify_update('openstack.network.v2.network.Network.update',
                           self.proxy.update_network)

    def test_port(self):
        self.verify_create('openstack.network.v2.port.Port.create',
                           self.proxy.create_port)
        self.verify_delete('openstack.network.v2.port.Port.delete',
                           self.proxy.delete_port)
        self.verify_find('openstack.network.v2.port.Port.find',
                         self.proxy.find_port)
        self.verify_get('openstack.network.v2.port.Port.get',
                        self.proxy.get_port)
        self.verify_list('openstack.network.v2.port.Port.list',
                         self.proxy.list_ports)
        self.verify_update('openstack.network.v2.port.Port.update',
                           self.proxy.update_port)

    def test_router(self):
        self.verify_create('openstack.network.v2.router.Router.create',
                           self.proxy.create_router)
        self.verify_delete('openstack.network.v2.router.Router.delete',
                           self.proxy.delete_router)
        self.verify_find('openstack.network.v2.router.Router.find',
                         self.proxy.find_router)
        self.verify_get('openstack.network.v2.router.Router.get',
                        self.proxy.get_router)
        self.verify_list('openstack.network.v2.router.Router.list',
                         self.proxy.list_routers)
        self.verify_update('openstack.network.v2.router.Router.update',
                           self.proxy.update_router)

    def test_subnet(self):
        self.verify_create('openstack.network.v2.subnet.Subnet.create',
                           self.proxy.create_subnet)
        self.verify_delete('openstack.network.v2.subnet.Subnet.delete',
                           self.proxy.delete_subnet)
        self.verify_find('openstack.network.v2.subnet.Subnet.find',
                         self.proxy.find_subnet)
        self.verify_get('openstack.network.v2.subnet.Subnet.get',
                        self.proxy.get_subnet)
        self.verify_list('openstack.network.v2.subnet.Subnet.list',
                         self.proxy.list_subnets)
        self.verify_update('openstack.network.v2.subnet.Subnet.update',
                           self.proxy.update_subnet)
