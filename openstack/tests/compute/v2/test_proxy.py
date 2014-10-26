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

    def test_flavor(self):
        self.verify_create('openstack.compute.v2.flavor.Flavor.create',
                           self.proxy.create_flavor)
        self.verify_delete('openstack.compute.v2.flavor.Flavor.delete',
                           self.proxy.delete_flavor)
        self.verify_find('openstack.compute.v2.flavor.Flavor.find',
                         self.proxy.find_flavor)
        self.verify_get('openstack.compute.v2.flavor.Flavor.get',
                        self.proxy.get_flavor)
        self.verify_list('openstack.compute.v2.flavor.Flavor.list',
                         self.proxy.list_flavors)
        self.verify_update('openstack.compute.v2.flavor.Flavor.update',
                           self.proxy.update_flavor)

    def test_keypair(self):
        self.verify_create('openstack.compute.v2.keypairs.Keypairs.create',
                           self.proxy.create_keypair)
        self.verify_delete('openstack.compute.v2.keypairs.Keypairs.delete',
                           self.proxy.delete_keypair)
        self.verify_find('openstack.compute.v2.keypairs.Keypairs.find',
                         self.proxy.find_keypair)
        self.verify_get('openstack.compute.v2.keypairs.Keypairs.get',
                        self.proxy.get_keypair)
        self.verify_list('openstack.compute.v2.keypairs.Keypairs.list',
                         self.proxy.list_keypairs)
        self.verify_update('openstack.compute.v2.keypairs.Keypairs.update',
                           self.proxy.update_keypair)

    def test_server(self):
        self.verify_create('openstack.compute.v2.server.Server.create',
                           self.proxy.create_server)
        self.verify_delete('openstack.compute.v2.server.Server.delete',
                           self.proxy.delete_server)
        self.verify_find('openstack.compute.v2.server.Server.find',
                         self.proxy.find_server)
        self.verify_get('openstack.compute.v2.server.Server.get',
                        self.proxy.get_server)
        self.verify_list('openstack.compute.v2.server.Server.list',
                         self.proxy.list_servers)
        self.verify_update('openstack.compute.v2.server.Server.update',
                           self.proxy.update_server)
