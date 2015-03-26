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
from openstack.compute.v2 import flavor
from openstack.compute.v2 import image
from openstack.compute.v2 import keypair
from openstack.compute.v2 import server
from openstack.compute.v2 import server_interface
from openstack.tests.unit import test_proxy_base


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
        self.verify_delete2(flavor.Flavor, self.proxy.delete_flavor, False)

    def test_flavor_delete_ignore(self):
        self.verify_delete2(flavor.Flavor, self.proxy.delete_flavor, True)

    def test_flavor_find(self):
        self.verify_find('openstack.compute.v2.flavor.Flavor.find',
                         self.proxy.find_flavor)

    def test_flavor_get(self):
        self.verify_get('openstack.compute.v2.flavor.Flavor.get',
                        self.proxy.get_flavor)

    def test_flavor_list_basic(self):
        self.verify_list('openstack.compute.v2.flavor.Flavor.list',
                         self.proxy.list_flavors,
                         method_kwargs={"details": False})

    def test_flavor_list_detail(self):
        self.verify_list('openstack.compute.v2.flavor.FlavorDetail.list',
                         self.proxy.list_flavors,
                         method_kwargs={"details": True})

    def test_flavor_update(self):
        self.verify_update('openstack.compute.v2.flavor.Flavor.update',
                           self.proxy.update_flavor)

    def test_image_delete(self):
        self.verify_delete2(image.Image, self.proxy.delete_image, False)

    def test_image_delete_ignore(self):
        self.verify_delete2(image.Image, self.proxy.delete_image, True)

    def test_image_find(self):
        self.verify_find('openstack.compute.v2.image.Image.find',
                         self.proxy.find_image)

    def test_image_get(self):
        self.verify_get('openstack.compute.v2.image.Image.get',
                        self.proxy.get_image)

    def test_image_list_basic(self):
        self.verify_list('openstack.compute.v2.image.Image.list',
                         self.proxy.list_images,
                         method_kwargs={"details": False},
                         expected_kwargs={"paginated": True})

    def test_image_list_detail(self):
        self.verify_list('openstack.compute.v2.image.ImageDetail.list',
                         self.proxy.list_images,
                         method_kwargs={"details": True},
                         expected_kwargs={"paginated": True})

    def test_keypair_create(self):
        self.verify_create('openstack.compute.v2.keypair.Keypair.create',
                           self.proxy.create_keypair)

    def test_keypair_delete(self):
        self.verify_delete2(keypair.Keypair, self.proxy.delete_keypair, False)

    def test_keypair_delete_ignore(self):
        self.verify_delete2(keypair.Keypair, self.proxy.delete_keypair, True)

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

    def test_limits(self):
        self.verify_get(
            'openstack.compute.v2.limits.Limits.get',
            self.proxy.limits)

    def test_server_interface_create(self):
        self.verify_create(
            'openstack.compute.v2.server_interface.ServerInterface.create',
            self.proxy.create_server_interface)

    def test_server_interface_delete(self):
        self.verify_delete2(server_interface.ServerInterface,
                            self.proxy.delete_server_interface, False)

    def test_server_interface_delete_ignore(self):
        self.verify_delete2(server_interface.ServerInterface,
                            self.proxy.delete_server_interface, True)

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

    def test_server_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_server,
                            method_kwargs=kwargs,
                            expected_args=[server.Server],
                            expected_kwargs=kwargs)

    def test_server_delete(self):
        self.verify_delete2(server.Server, self.proxy.delete_server, False)

    def test_server_delete_ignore(self):
        self.verify_delete2(server.Server, self.proxy.delete_server, True)

    def test_server_find(self):
        self.verify_find('openstack.compute.v2.server.Server.find',
                         self.proxy.find_server)

    def test_server_get(self):
        self.verify_get('openstack.compute.v2.server.Server.get',
                        self.proxy.get_server)

    def test_server_list(self):
        self.verify_list('openstack.compute.v2.server.Server.list',
                         self.proxy.list_servers,
                         expected_kwargs={"paginated": True})

    def test_server_update(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_server,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[server.Server, "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_server_wait_for(self):
        value = server.Server(attrs={'id': '1234'})
        self.verify_wait_for_status(
            'openstack.resource.wait_for_status',
            self.proxy.wait_for_server,
            method_args=[value],
            expected_args=[value, 'ACTIVE', ['ERROR'], 2, 120])
