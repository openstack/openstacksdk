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
from openstack.compute.v2 import service
from openstack.tests.unit import test_proxy_base2


class TestComputeProxy(test_proxy_base2.TestProxyBase):
    def setUp(self):
        super(TestComputeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_extension_find(self):
        self.verify_find(self.proxy.find_extension, extension.Extension)

    def test_extensions(self):
        self.verify_list_no_kwargs(self.proxy.extensions, extension.Extension,
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
        self.verify_list_no_kwargs(self.proxy.keypairs, keypair.Keypair,
                                   paginated=False)

    def test_limits_get(self):
        self.verify_get(self.proxy.get_limits, limits.Limits, value=[])

    def test_server_interface_create(self):
        self.verify_create(self.proxy.create_server_interface,
                           server_interface.ServerInterface,
                           method_kwargs={"server": "test_id"},
                           expected_kwargs={"server_id": "test_id"})

    def test_server_interface_delete(self):
        self.proxy._get_uri_attribute = lambda *args: args[1]

        interface_id = "test_interface_id"
        server_id = "test_server_id"
        test_interface = server_interface.ServerInterface(id=interface_id)
        test_interface.server_id = server_id

        # Case1: ServerInterface instance is provided as value
        self._verify2("openstack.proxy2.BaseProxy._delete",
                      self.proxy.delete_server_interface,
                      method_args=[test_interface],
                      method_kwargs={"server": server_id},
                      expected_args=[server_interface.ServerInterface],
                      expected_kwargs={"server_id": server_id,
                                       "port_id": interface_id,
                                       "ignore_missing": True})

        # Case2: ServerInterface ID is provided as value
        self._verify2("openstack.proxy2.BaseProxy._delete",
                      self.proxy.delete_server_interface,
                      method_args=[interface_id],
                      method_kwargs={"server": server_id},
                      expected_args=[server_interface.ServerInterface],
                      expected_kwargs={"server_id": server_id,
                                       "port_id": interface_id,
                                       "ignore_missing": True})

    def test_server_interface_delete_ignore(self):
        self.proxy._get_uri_attribute = lambda *args: args[1]
        self.verify_delete(self.proxy.delete_server_interface,
                           server_interface.ServerInterface, True,
                           method_kwargs={"server": "test_id"},
                           expected_args=[server_interface.ServerInterface],
                           expected_kwargs={"server_id": "test_id",
                                            "port_id": "resource_or_id"})

    def test_server_interface_get(self):
        self.proxy._get_uri_attribute = lambda *args: args[1]

        interface_id = "test_interface_id"
        server_id = "test_server_id"
        test_interface = server_interface.ServerInterface(id=interface_id)
        test_interface.server_id = server_id

        # Case1: ServerInterface instance is provided as value
        self._verify2('openstack.proxy2.BaseProxy._get',
                      self.proxy.get_server_interface,
                      method_args=[test_interface],
                      method_kwargs={"server": server_id},
                      expected_args=[server_interface.ServerInterface],
                      expected_kwargs={"port_id": interface_id,
                                       "server_id": server_id})

        # Case2: ServerInterface ID is provided as value
        self._verify2('openstack.proxy2.BaseProxy._get',
                      self.proxy.get_server_interface,
                      method_args=[interface_id],
                      method_kwargs={"server": server_id},
                      expected_args=[server_interface.ServerInterface],
                      expected_kwargs={"port_id": interface_id,
                                       "server_id": server_id})

    def test_server_interfaces(self):
        self.verify_list(self.proxy.server_interfaces,
                         server_interface.ServerInterface,
                         paginated=False, method_args=["test_id"],
                         expected_kwargs={"server_id": "test_id"})

    def test_server_ips_with_network_label(self):
        self.verify_list(self.proxy.server_ips, server_ip.ServerIP,
                         paginated=False, method_args=["test_id"],
                         method_kwargs={"network_label": "test_label"},
                         expected_kwargs={"server_id": "test_id",
                                          "network_label": "test_label"})

    def test_server_ips_without_network_label(self):
        self.verify_list(self.proxy.server_ips, server_ip.ServerIP,
                         paginated=False, method_args=["test_id"],
                         expected_kwargs={"server_id": "test_id",
                                          "network_label": None})

    def test_server_create_attrs(self):
        self.verify_create(self.proxy.create_server, server.Server)

    def test_server_delete(self):
        self.verify_delete(self.proxy.delete_server, server.Server, False)

    def test_server_delete_ignore(self):
        self.verify_delete(self.proxy.delete_server, server.Server, True)

    def test_server_force_delete(self):
        self._verify("openstack.compute.v2.server.Server.force_delete",
                     self.proxy.delete_server,
                     method_args=["value", False, True])

    def test_server_find(self):
        self.verify_find(self.proxy.find_server, server.Server)

    def test_server_get(self):
        self.verify_get(self.proxy.get_server, server.Server)

    def test_servers_detailed(self):
        self.verify_list(self.proxy.servers, server.ServerDetail,
                         paginated=True,
                         method_kwargs={"details": True,
                                        "changes_since": 1, "image": 2},
                         expected_kwargs={"changes_since": 1, "image": 2})

    def test_servers_not_detailed(self):
        self.verify_list(self.proxy.servers, server.Server,
                         paginated=True,
                         method_kwargs={"details": False,
                                        "changes_since": 1, "image": 2},
                         expected_kwargs={"paginated": True,
                                          "changes_since": 1, "image": 2})

    def test_server_update(self):
        self.verify_update(self.proxy.update_server, server.Server)

    def test_server_wait_for(self):
        value = server.Server(id='1234')
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
                     self.proxy.confirm_server_resize,
                     method_args=["value"])

    def test_server_revert_resize(self):
        self._verify("openstack.compute.v2.server.Server.revert_resize",
                     self.proxy.revert_server_resize,
                     method_args=["value"])

    def test_server_rebuild(self):
        id = 'test_image_id'
        image_obj = image.Image(id='test_image_id')

        # Case1: image object is provided
        # NOTE: Inside of Server.rebuild is where image_obj gets converted
        # to an ID instead of object.
        self._verify('openstack.compute.v2.server.Server.rebuild',
                     self.proxy.rebuild_server,
                     method_args=["value", "test_server", "test_pass"],
                     method_kwargs={"metadata": {"k1": "v1"},
                                    "image": image_obj},
                     expected_args=["test_server", "test_pass"],
                     expected_kwargs={"metadata": {"k1": "v1"},
                                      "image": image_obj})

        # Case2: image name or id is provided
        self._verify('openstack.compute.v2.server.Server.rebuild',
                     self.proxy.rebuild_server,
                     method_args=["value", "test_server", "test_pass"],
                     method_kwargs={"metadata": {"k1": "v1"},
                                    "image": id},
                     expected_args=["test_server", "test_pass"],
                     expected_kwargs={"metadata": {"k1": "v1"},
                                      "image": id})

    def test_add_fixed_ip_to_server(self):
        self._verify("openstack.compute.v2.server.Server.add_fixed_ip",
                     self.proxy.add_fixed_ip_to_server,
                     method_args=["value", "network-id"],
                     expected_args=["network-id"])

    def test_fixed_ip_from_server(self):
        self._verify("openstack.compute.v2.server.Server.remove_fixed_ip",
                     self.proxy.remove_fixed_ip_from_server,
                     method_args=["value", "address"],
                     expected_args=["address"])

    def test_floating_ip_to_server(self):
        self._verify("openstack.compute.v2.server.Server.add_floating_ip",
                     self.proxy.add_floating_ip_to_server,
                     method_args=["value", "floating-ip"],
                     expected_args=["floating-ip"],
                     expected_kwargs={'fixed_address': None})

    def test_add_floating_ip_to_server_with_fixed_addr(self):
        self._verify("openstack.compute.v2.server.Server.add_floating_ip",
                     self.proxy.add_floating_ip_to_server,
                     method_args=["value", "floating-ip", 'fixed-addr'],
                     expected_args=["floating-ip"],
                     expected_kwargs={'fixed_address': 'fixed-addr'})

    def test_remove_floating_ip_from_server(self):
        self._verify("openstack.compute.v2.server.Server.remove_floating_ip",
                     self.proxy.remove_floating_ip_from_server,
                     method_args=["value", "address"],
                     expected_args=["address"])

    def test_server_backup(self):
        self._verify("openstack.compute.v2.server.Server.backup",
                     self.proxy.backup_server,
                     method_args=["value", "name", "daily", 1],
                     expected_args=["name", "daily", 1])

    def test_server_pause(self):
        self._verify("openstack.compute.v2.server.Server.pause",
                     self.proxy.pause_server,
                     method_args=["value"])

    def test_server_unpause(self):
        self._verify("openstack.compute.v2.server.Server.unpause",
                     self.proxy.unpause_server,
                     method_args=["value"])

    def test_server_suspend(self):
        self._verify("openstack.compute.v2.server.Server.suspend",
                     self.proxy.suspend_server,
                     method_args=["value"])

    def test_server_resume(self):
        self._verify("openstack.compute.v2.server.Server.resume",
                     self.proxy.resume_server,
                     method_args=["value"])

    def test_server_lock(self):
        self._verify("openstack.compute.v2.server.Server.lock",
                     self.proxy.lock_server,
                     method_args=["value"])

    def test_server_unlock(self):
        self._verify("openstack.compute.v2.server.Server.unlock",
                     self.proxy.unlock_server,
                     method_args=["value"])

    def test_server_rescue(self):
        self._verify("openstack.compute.v2.server.Server.rescue",
                     self.proxy.rescue_server,
                     method_args=["value"],
                     expected_kwargs={"admin_pass": None, "image_ref": None})

    def test_server_rescue_with_options(self):
        self._verify("openstack.compute.v2.server.Server.rescue",
                     self.proxy.rescue_server,
                     method_args=["value", 'PASS', 'IMG'],
                     expected_kwargs={"admin_pass": 'PASS',
                                      "image_ref": 'IMG'})

    def test_server_unrescue(self):
        self._verify("openstack.compute.v2.server.Server.unrescue",
                     self.proxy.unrescue_server,
                     method_args=["value"])

    def test_server_evacuate(self):
        self._verify("openstack.compute.v2.server.Server.evacuate",
                     self.proxy.evacuate_server,
                     method_args=["value"],
                     expected_kwargs={"host": None, "admin_pass": None,
                                      "force": None})

    def test_server_evacuate_with_options(self):
        self._verify("openstack.compute.v2.server.Server.evacuate",
                     self.proxy.evacuate_server,
                     method_args=["value", 'HOST2', 'NEW_PASS', True],
                     expected_kwargs={"host": "HOST2",
                                      "admin_pass": 'NEW_PASS',
                                      "force": True})

    def test_server_start(self):
        self._verify("openstack.compute.v2.server.Server.start",
                     self.proxy.start_server,
                     method_args=["value"])

    def test_server_stop(self):
        self._verify("openstack.compute.v2.server.Server.stop",
                     self.proxy.stop_server,
                     method_args=["value"])

    def test_server_shelve(self):
        self._verify("openstack.compute.v2.server.Server.shelve",
                     self.proxy.shelve_server,
                     method_args=["value"])

    def test_server_unshelve(self):
        self._verify("openstack.compute.v2.server.Server.unshelve",
                     self.proxy.unshelve_server,
                     method_args=["value"])

    def test_get_server_output(self):
        self._verify("openstack.compute.v2.server.Server.get_console_output",
                     self.proxy.get_server_console_output,
                     method_args=["value"],
                     expected_kwargs={"length": None})

        self._verify("openstack.compute.v2.server.Server.get_console_output",
                     self.proxy.get_server_console_output,
                     method_args=["value", 1],
                     expected_kwargs={"length": 1})

    def test_availability_zones(self):
        self.verify_list_no_kwargs(self.proxy.availability_zones,
                                   az.AvailabilityZone,
                                   paginated=False)

    def test_get_all_server_metadata(self):
        self._verify2("openstack.compute.v2.server.Server.get_metadata",
                      self.proxy.get_server_metadata,
                      method_args=["value"],
                      method_result=server.Server(id="value", metadata={}),
                      expected_args=[self.session],
                      expected_result={})

    def test_set_server_metadata(self):
        kwargs = {"a": "1", "b": "2"}
        id = "an_id"
        self._verify2("openstack.compute.v2.server.Server.set_metadata",
                      self.proxy.set_server_metadata,
                      method_args=[id],
                      method_kwargs=kwargs,
                      method_result=server.Server.existing(id=id,
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
        self.verify_list_no_kwargs(self.proxy.hypervisors,
                                   hypervisor.Hypervisor,
                                   paginated=False)

    def test_find_hypervisor(self):
        self.verify_find(self.proxy.find_hypervisor,
                         hypervisor.Hypervisor)

    def test_get_hypervisor(self):
        self.verify_get(self.proxy.get_hypervisor,
                        hypervisor.Hypervisor)

    def test_services(self):
        self.verify_list_no_kwargs(self.proxy.services,
                                   service.Service,
                                   paginated=False)

    def test_enable_service(self):
        self._verify('openstack.compute.v2.service.Service.enable',
                     self.proxy.enable_service,
                     method_args=["value", "host1", "nova-compute"],
                     expected_args=["host1", "nova-compute"])

    def test_disable_service(self):
        self._verify('openstack.compute.v2.service.Service.disable',
                     self.proxy.disable_service,
                     method_args=["value", "host1", "nova-compute"],
                     expected_args=["host1", "nova-compute", None])

    def test_force_service_down(self):
        self._verify('openstack.compute.v2.service.Service.force_down',
                     self.proxy.force_service_down,
                     method_args=["value", "host1", "nova-compute"],
                     expected_args=["host1", "nova-compute"])

    def test_live_migrate_server(self):
        self._verify('openstack.compute.v2.server.Server.live_migrate',
                     self.proxy.live_migrate_server,
                     method_args=["value", "host1", "force"],
                     expected_args=["host1", "force"])
