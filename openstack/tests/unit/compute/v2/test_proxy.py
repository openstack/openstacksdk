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
from openstack.compute.v2 import extension
from openstack.compute.v2 import flavor
from openstack.compute.v2 import image
from openstack.compute.v2 import keypair
from openstack.compute.v2 import limits
from openstack.compute.v2 import server
from openstack.compute.v2 import server_interface
from openstack.compute.v2 import server_ip
from openstack.tests.unit import test_proxy_base


class TestComputeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestComputeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_extension_find(self):
        self.verify_find('openstack.compute.v2.extension.Extension.find',
                         self.proxy.find_extension)

    def test_extensions(self):
        self.verify_list2(self.proxy.extensions,
                          expected_args=[extension.Extension],
                          expected_kwargs={"paginated": False})

    def test_flavor_create(self):
        self.verify_create(self.proxy.create_flavor, flavor.Flavor)

    def test_flavor_delete(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, False)

    def test_flavor_delete_ignore(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, True)

    def test_flavor_find(self):
        self.verify_find('openstack.compute.v2.flavor.Flavor.find',
                         self.proxy.find_flavor)

    def test_flavor_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_flavor,
                         method_args=["resource_or_id"],
                         expected_args=[flavor.Flavor, "resource_or_id"])

    def test_flavors_detailed(self):
        self.verify_list2(self.proxy.flavors,
                          method_kwargs={"details": True, "query": 1},
                          expected_args=[flavor.FlavorDetail],
                          expected_kwargs={"paginated": True, "query": 1})

    def test_flavors_not_detailed(self):
        self.verify_list2(self.proxy.flavors,
                          method_kwargs={"details": False, "query": 1},
                          expected_args=[flavor.Flavor],
                          expected_kwargs={"paginated": True, "query": 1})

    def test_flavor_update(self):
        self.verify_update(self.proxy.update_flavor, flavor.Flavor)

    def test_image_delete(self):
        self.verify_delete(self.proxy.delete_image, image.Image, False)

    def test_image_delete_ignore(self):
        self.verify_delete(self.proxy.delete_image, image.Image, True)

    def test_image_find(self):
        self.verify_find('openstack.compute.v2.image.Image.find',
                         self.proxy.find_image)

    def test_image_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_image,
                         method_args=["resource_or_id"],
                         expected_args=[image.Image, "resource_or_id"])

    def test_images_detailed(self):
        self.verify_list2(self.proxy.images,
                          method_kwargs={"details": True, "query": 1},
                          expected_args=[image.ImageDetail],
                          expected_kwargs={"paginated": True, "query": 1})

    def test_images_not_detailed(self):
        self.verify_list2(self.proxy.images,
                          method_kwargs={"details": False, "query": 1},
                          expected_args=[image.Image],
                          expected_kwargs={"paginated": True, "query": 1})

    def test_keypair_create(self):
        self.verify_create(self.proxy.create_keypair, keypair.Keypair)

    def test_keypair_delete(self):
        self.verify_delete(self.proxy.delete_keypair, keypair.Keypair, False)

    def test_keypair_delete_ignore(self):
        self.verify_delete(self.proxy.delete_keypair, keypair.Keypair, True)

    def test_keypair_find(self):
        self.verify_find('openstack.compute.v2.keypair.Keypair.find',
                         self.proxy.find_keypair)

    def test_keypair_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_keypair,
                         method_args=["resource_or_id"],
                         expected_args=[keypair.Keypair, "resource_or_id"])

    def test_keypairs(self):
        self.verify_list2(self.proxy.keypairs,
                          expected_args=[keypair.Keypair],
                          expected_kwargs={"paginated": False})

    def test_keypair_update(self):
        self.verify_update(self.proxy.update_keypair, keypair.Keypair)

    def test_limits_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_limits,
                         expected_args=[limits.Limits])

    def test_server_interface_create(self):
        self.verify_create(self.proxy.create_server_interface,
                           server_interface.ServerInterface)

    def test_server_interface_delete(self):
        self.verify_delete(self.proxy.delete_server_interface,
                           server_interface.ServerInterface, False)

    def test_server_interface_delete_ignore(self):
        self.verify_delete(self.proxy.delete_server_interface,
                           server_interface.ServerInterface, True)

    def test_server_interface_find(self):
        self.verify_find(
            'openstack.compute.v2.server_interface.ServerInterface.find',
            self.proxy.find_server_interface)

    def test_server_interface_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_server_interface,
                         method_args=["resource_or_id"],
                         expected_args=[server_interface.ServerInterface,
                                        "resource_or_id"])

    def test_server_interfaces(self):
        self.verify_list2(self.proxy.server_interfaces,
                          expected_args=[server_interface.ServerInterface],
                          expected_kwargs={"paginated": False})

    def test_server_interface_update(self):
        self.verify_update(self.proxy.update_server_interface,
                           server_interface.ServerInterface)

    def test_server_ip_find(self):
        self.verify_find('openstack.compute.v2.server_ip.ServerIP.find',
                         self.proxy.find_server_ip)

    def test_server_ips(self):
        self.verify_list2(self.proxy.server_ips,
                          expected_args=[server_ip.ServerIP],
                          expected_kwargs={"paginated": False})

    def test_server_create_attrs(self):
        self.verify_create(self.proxy.create_server, server.Server)

    def test_server_delete(self):
        self.verify_delete(self.proxy.delete_server, server.Server, False)

    def test_server_delete_ignore(self):
        self.verify_delete(self.proxy.delete_server, server.Server, True)

    def test_server_find(self):
        self.verify_find('openstack.compute.v2.server.Server.find',
                         self.proxy.find_server)

    def test_server_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_server,
                         method_args=["resource_or_id"],
                         expected_args=[server.Server, "resource_or_id"])

    def test_servers_detailed(self):
        self.verify_list2(self.proxy.servers,
                          method_args=[True],
                          method_kwargs={"changes_since": 1, "image": 2},
                          expected_args=[server.ServerDetail],
                          expected_kwargs={"paginated": True,
                                           "changes-since": 1, "image": 2})

    def test_servers_not_detailed(self):
        self.verify_list2(self.proxy.servers,
                          method_args=[False],
                          method_kwargs={"changes_since": 1, "image": 2},
                          expected_args=[server.Server],
                          expected_kwargs={"paginated": True,
                                           "changes-since": 1, "image": 2})

    def test_server_update(self):
        self.verify_update(self.proxy.update_server, server.Server)

    def test_server_wait_for(self):
        value = server.Server(attrs={'id': '1234'})
        self.verify_wait_for_status(
            'openstack.resource.wait_for_status',
            self.proxy.wait_for_server,
            method_args=[value],
            expected_args=[value, 'ACTIVE', ['ERROR'], 2, 120])
