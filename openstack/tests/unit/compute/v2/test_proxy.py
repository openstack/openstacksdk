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

from openstack.compute.v2 import _proxy
from openstack.compute.v2 import availability_zone as az
from openstack.compute.v2 import extension
from openstack.compute.v2 import flavor
from openstack.compute.v2 import hypervisor
from openstack.compute.v2 import image
from openstack.compute.v2 import keypair
from openstack.compute.v2 import limits
from openstack.compute.v2 import server
from openstack.compute.v2 import server_group
from openstack.compute.v2 import server_interface
from openstack.compute.v2 import server_ip
from openstack.tests.unit import test_proxy_base


class TestComputeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestComputeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_extension_find(self):
        self.verify_find(self.proxy.find_extension, extension.Extension)

    def test_extensions(self):
        self.verify_list(self.proxy.extensions, extension.Extension,
                         paginated=False)

    def test_flavor_create(self):
        self.verify_create(self.proxy.create_flavor, flavor.Flavor)

    def test_flavor_delete(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, False)

    def test_flavor_delete_ignore(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, True)

    def test_flavor_find(self):
        self.verify_find(self.proxy.find_flavor, flavor.Flavor)

    def test_flavor_get(self):
        self.verify_get(self.proxy.get_flavor, flavor.Flavor)

    def test_flavors_detailed(self):
        self.verify_list(self.proxy.flavors, flavor.FlavorDetail,
                         paginated=True,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_flavors_not_detailed(self):
        self.verify_list(self.proxy.flavors, flavor.Flavor,
                         paginated=True,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    def test_flavor_update(self):
        self.verify_update(self.proxy.update_flavor, flavor.Flavor)

    def test_image_delete(self):
        self.verify_delete(self.proxy.delete_image, image.Image, False)

    def test_image_delete_ignore(self):
        self.verify_delete(self.proxy.delete_image, image.Image, True)

    def test_image_find(self):
        self.verify_find(self.proxy.find_image, image.Image)

    def test_image_get(self):
        self.verify_get(self.proxy.get_image, image.Image)

    def test_images_detailed(self):
        self.verify_list(self.proxy.images, image.ImageDetail,
                         paginated=True,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_images_not_detailed(self):
        self.verify_list(self.proxy.images, image.Image,
                         paginated=True,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    def test_keypair_create(self):
        self.verify_create(self.proxy.create_keypair, keypair.Keypair)

    def test_keypair_delete(self):
        self.verify_delete(self.proxy.delete_keypair, keypair.Keypair, False)

    def test_keypair_delete_ignore(self):
        self.verify_delete(self.proxy.delete_keypair, keypair.Keypair, True)

    def test_keypair_find(self):
        self.verify_find(self.proxy.find_keypair, keypair.Keypair)

    def test_keypair_get(self):
        self.verify_get(self.proxy.get_keypair, keypair.Keypair)

    def test_keypairs(self):
        self.verify_list(self.proxy.keypairs, keypair.Keypair,
                         paginated=False)

    def test_keypair_update(self):
        self.verify_update(self.proxy.update_keypair, keypair.Keypair)

    def test_limits_get(self):
        self.verify_get(self.proxy.get_limits, limits.Limits, value=[])

    def test_server_interface_create(self):
        self.verify_create(self.proxy.create_server_interface,
                           server_interface.ServerInterface,
                           method_kwargs={"server": "test_id"},
                           expected_kwargs={"path_args": {
                               "server_id": "test_id"}})

    def test_server_interface_delete(self):
        test_interface = server_interface.ServerInterface.from_id(
            "test_interface_id")
        test_interface.server_id = "test_server_id"

        # Case1: ServerInterface instance is provided as value
        self._verify2("openstack.proxy.BaseProxy._delete",
                      self.proxy.delete_server_interface,
                      method_args=[test_interface, "test_server_id"],
                      expected_args=[server_interface.ServerInterface,
                                     test_interface],
                      expected_kwargs={"path_args": {
                          "server_id": "test_server_id"},
                          "ignore_missing": True})

        # Case2: ServerInterface ID is provided as value
        self._verify2("openstack.proxy.BaseProxy._delete",
                      self.proxy.delete_server_interface,
                      method_args=["test_interface_id", "test_server_id"],
                      expected_args=[server_interface.ServerInterface,
                                     "test_interface_id"],
                      expected_kwargs={"path_args": {
                          "server_id": "test_server_id"},
                          "ignore_missing": True})

    def test_server_interface_delete_ignore(self):
        self.verify_delete(self.proxy.delete_server_interface,
                           server_interface.ServerInterface, True,
                           {"server": "test_id"}, {"server_id": "test_id"})

    def test_server_interface_get(self):
        test_interface = server_interface.ServerInterface.from_id(
            "test_interface_id")
        test_interface.server_id = "test_server_id"

        # Case1: ServerInterface instance is provided as value
        self._verify2('openstack.proxy.BaseProxy._get',
                      self.proxy.get_server_interface,
                      method_args=[test_interface, "test_id"],
                      expected_args=[server_interface.ServerInterface,
                                     test_interface],
                      expected_kwargs={"path_args": {
                          "server_id": "test_server_id"}})

        # Case2: ServerInterface ID is provided as value
        self._verify2('openstack.proxy.BaseProxy._get',
                      self.proxy.get_server_interface,
                      method_args=["test_interface_id", "test_server_id"],
                      expected_args=[server_interface.ServerInterface,
                                     "test_interface_id"],
                      expected_kwargs={"path_args": {
                          "server_id": "test_server_id"}})

    def test_server_interfaces(self):
        self.verify_list(self.proxy.server_interfaces,
                         server_interface.ServerInterface,
                         paginated=False, method_args=["test_id"],
                         expected_kwargs={"path_args": {
                             "server_id": "test_id"}})

    def test_server_ip_find(self):
        self.verify_find(self.proxy.find_server_ip, server_ip.ServerIP)

    def test_server_ips(self):
        self.verify_list(self.proxy.server_ips, server_ip.ServerIP,
                         paginated=False)

    def test_server_create_attrs(self):
        self.verify_create(self.proxy.create_server, server.Server)

    def test_server_delete(self):
        self.verify_delete(self.proxy.delete_server, server.Server, False)

    def test_server_delete_ignore(self):
        self.verify_delete(self.proxy.delete_server, server.Server, True)

    def test_server_find(self):
        self.verify_find(self.proxy.find_server, server.Server)

    def test_server_get(self):
        self.verify_get(self.proxy.get_server, server.Server)

    def test_servers_detailed(self):
        self.verify_list(self.proxy.servers, server.ServerDetail,
                         paginated=True,
                         method_kwargs={"details": True,
                                        "changes_since": 1, "image": 2},
                         expected_kwargs={"changes-since": 1, "image": 2})

    def test_servers_not_detailed(self):
        self.verify_list(self.proxy.servers, server.Server,
                         paginated=True,
                         method_kwargs={"details": False,
                                        "changes_since": 1, "image": 2},
                         expected_kwargs={"paginated": True,
                                          "changes-since": 1, "image": 2})

    def test_server_update(self):
        self.verify_update(self.proxy.update_server, server.Server)

    def test_server_wait_for(self):
        value = server.Server(attrs={'id': '1234'})
        self.verify_wait_for_status(
            self.proxy.wait_for_server,
            method_args=[value],
            expected_args=[value, 'ACTIVE', ['ERROR'], 2, 120])

    def test_server_resize(self):
        self._verify("openstack.compute.v2.server.Server.resize",
                     self.proxy.resize_server,
                     method_args=["value", "test-flavor"],
                     expected_args=["test-flavor"])

    def test_server_confirm_resize(self):
        self._verify("openstack.compute.v2.server.Server.confirm_resize",
                     self.proxy.confirm_resize_server,
                     method_args=["value"])

    def test_server_revert_resize(self):
        self._verify("openstack.compute.v2.server.Server.revert_resize",
                     self.proxy.revert_resize_server,
                     method_args=["value"])

    @mock.patch.object(_proxy.Proxy, 'find_image')
    def test_server_rebuild(self, mock_find_image):
        image_obj = image.Image.from_id('test_image_id')
        mock_find_image.side_effect = [image_obj, None]

        # Case1: image object is provided as image_ref
        self._verify('openstack.compute.v2.server.Server.rebuild',
                     self.proxy.rebuild_server,
                     method_args=["value", image_obj, "test_server",
                                  "test_pass"],
                     method_kwargs={"metadata": {"k1": "v1"}},
                     expected_args=["test_server", "test_image_id",
                                    "test_pass"],
                     expected_kwargs={"metadata": {"k1": "v1"}})

        # Case2: image name or id is provided as image_ref
        self._verify('openstack.compute.v2.server.Server.rebuild',
                     self.proxy.rebuild_server,
                     method_args=["value", "test_image_name_or_id",
                                  "test_server", "test_pass"],
                     method_kwargs={"metadata": {"k1": "v1"}},
                     expected_args=["test_server", "test_image_id",
                                    "test_pass"],
                     expected_kwargs={"metadata": {"k1": "v1"}})

        # Case3: image URL is provided as image_ref
        self._verify('openstack.compute.v2.server.Server.rebuild',
                     self.proxy.rebuild_server,
                     method_args=["value", "test_image_url", "test_server",
                                  "test_pass"],
                     method_kwargs={"metadata": {"k1": "v1"}},
                     expected_args=["test_server", "test_image_url",
                                    "test_pass"],
                     expected_kwargs={"metadata": {"k1": "v1"}})

    def test_availability_zones(self):
        self.verify_list(self.proxy.availability_zones, az.AvailabilityZone,
                         paginated=False)

    def test_get_all_server_metadata(self):
        self._verify2("openstack.compute.v2.server.Server.get_metadata",
                      self.proxy.get_server_metadata,
                      method_args=["value"],
                      method_result=server.Server.existing(id="value",
                                                           metadata={}),
                      expected_args=[self.session],
                      expected_result={})

    def test_set_server_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        self._verify2("openstack.compute.v2.server.Server.set_metadata",
                      self.proxy.set_server_metadata,
                      method_args=["value"],
                      method_kwargs=kwargs,
                      method_result=server.Server.existing(id="value",
                                                           metadata=kwargs),
                      expected_args=[self.session],
                      expected_kwargs=kwargs,
                      expected_result=kwargs)

    def test_delete_server_metadata(self):
        self._verify2("openstack.compute.v2.server.Server.delete_metadata",
                      self.proxy.delete_server_metadata,
                      expected_result=None,
                      method_args=["value", "key"],
                      expected_args=[self.session, "key"])

    def test_server_group_create(self):
        self.verify_create(self.proxy.create_server_group,
                           server_group.ServerGroup)

    def test_server_group_delete(self):
        self.verify_delete(self.proxy.delete_server_group,
                           server_group.ServerGroup, False)

    def test_server_group_delete_ignore(self):
        self.verify_delete(self.proxy.delete_server_group,
                           server_group.ServerGroup, True)

    def test_server_group_find(self):
        self.verify_find(self.proxy.find_server_group,
                         server_group.ServerGroup)

    def test_server_group_get(self):
        self.verify_get(self.proxy.get_server_group,
                        server_group.ServerGroup)

    def test_server_groups(self):
        self.verify_list(self.proxy.server_groups, server_group.ServerGroup,
                         paginated=False)

    def test_hypervisors(self):
        self.verify_list(self.proxy.hypervisors, hypervisor.Hypervisor,
                         paginated=False)

    def test_find_hypervisor(self):
        self.verify_find(self.proxy.find_hypervisor,
                         hypervisor.Hypervisor)

    def test_get_hypervisor(self):
        self.verify_get(self.proxy.get_hypervisor,
                        hypervisor.Hypervisor)
