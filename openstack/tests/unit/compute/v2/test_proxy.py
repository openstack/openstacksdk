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
from unittest import mock

from openstack.compute.v2 import _proxy
from openstack.compute.v2 import aggregate
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
from openstack.compute.v2 import server_remote_console
from openstack.compute.v2 import service
from openstack.tests.unit import test_proxy_base


class TestComputeProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestComputeProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestFlavor(TestComputeProxy):
    def test_flavor_create(self):
        self.verify_create(self.proxy.create_flavor, flavor.Flavor)

    def test_flavor_delete(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, False)

    def test_flavor_update(self):
        self.verify_update(self.proxy.update_flavor, flavor.Flavor, False)

    def test_flavor_delete_ignore(self):
        self.verify_delete(self.proxy.delete_flavor, flavor.Flavor, True)

    def test_flavor_find(self):
        self.verify_find(self.proxy.find_flavor, flavor.Flavor)

    def test_flavor_find_query(self):
        self.verify_find(
            self.proxy.find_flavor, flavor.Flavor,
            method_kwargs={"a": "b"},
            expected_kwargs={"a": "b", "ignore_missing": False}
        )

    def test_flavor_find_fetch_extra(self):
        """fetch extra_specs is triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor()
            mocked.return_value = res
            self._verify2(
                'openstack.proxy.Proxy._find',
                self.proxy.find_flavor,
                method_args=['res', True, True],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res'],
                expected_kwargs={'ignore_missing': True}
            )
            mocked.assert_called_once()

    def test_flavor_find_skip_fetch_extra(self):
        """fetch extra_specs not triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor(extra_specs={'a': 'b'})
            mocked.return_value = res
            self._verify2(
                'openstack.proxy.Proxy._find',
                self.proxy.find_flavor,
                method_args=['res', True],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res'],
                expected_kwargs={'ignore_missing': True}
            )
            mocked.assert_not_called()

    def test_flavor_get_no_extra(self):
        """fetch extra_specs not triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor()
            mocked.return_value = res
            self._verify2(
                'openstack.proxy.Proxy._get',
                self.proxy.get_flavor,
                method_args=['res'],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res']
            )
            mocked.assert_not_called()

    def test_flavor_get_fetch_extra(self):
        """fetch extra_specs is triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor()
            mocked.return_value = res
            self._verify2(
                'openstack.proxy.Proxy._get',
                self.proxy.get_flavor,
                method_args=['res', True],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res']
            )
            mocked.assert_called_once()

    def test_flavor_get_skip_fetch_extra(self):
        """fetch extra_specs not triggered"""
        with mock.patch(
            'openstack.compute.v2.flavor.Flavor.fetch_extra_specs'
        ) as mocked:
            res = flavor.Flavor(extra_specs={'a': 'b'})
            mocked.return_value = res
            self._verify2(
                'openstack.proxy.Proxy._get',
                self.proxy.get_flavor,
                method_args=['res', True],
                expected_result=res,
                expected_args=[flavor.Flavor, 'res']
            )
            mocked.assert_not_called()

    @mock.patch("openstack.proxy.Proxy._list", auto_spec=True)
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs",
                auto_spec=True)
    def test_flavors_detailed(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=True)
        for r in res:
            self.assertIsNotNone(r)
        fetch_mock.assert_not_called()
        list_mock.assert_called_with(
            flavor.Flavor,
            base_path="/flavors/detail"
        )

    @mock.patch("openstack.proxy.Proxy._list", auto_spec=True)
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs",
                auto_spec=True)
    def test_flavors_not_detailed(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=False)
        for r in res:
            self.assertIsNotNone(r)
        fetch_mock.assert_not_called()
        list_mock.assert_called_with(
            flavor.Flavor,
            base_path="/flavors"
        )

    @mock.patch("openstack.proxy.Proxy._list", auto_spec=True)
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs",
                auto_spec=True)
    def test_flavors_query(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=False, get_extra_specs=True, a="b")
        for r in res:
            fetch_mock.assert_called_with(self.proxy)
        list_mock.assert_called_with(
            flavor.Flavor,
            base_path="/flavors",
            a="b"
        )

    @mock.patch("openstack.proxy.Proxy._list", auto_spec=True)
    @mock.patch("openstack.compute.v2.flavor.Flavor.fetch_extra_specs",
                auto_spec=True)
    def test_flavors_get_extra(self, fetch_mock, list_mock):
        res = self.proxy.flavors(details=False, get_extra_specs=True)
        for r in res:
            fetch_mock.assert_called_with(self.proxy)
        list_mock.assert_called_with(
            flavor.Flavor,
            base_path="/flavors"
        )

    def test_flavor_get_access(self):
        self._verify("openstack.compute.v2.flavor.Flavor.get_access",
                     self.proxy.get_flavor_access,
                     method_args=["value"],
                     expected_args=[])

    def test_flavor_add_tenant_access(self):
        self._verify("openstack.compute.v2.flavor.Flavor.add_tenant_access",
                     self.proxy.flavor_add_tenant_access,
                     method_args=["value", "fake-tenant"],
                     expected_args=["fake-tenant"])

    def test_flavor_remove_tenant_access(self):
        self._verify("openstack.compute.v2.flavor.Flavor.remove_tenant_access",
                     self.proxy.flavor_remove_tenant_access,
                     method_args=["value", "fake-tenant"],
                     expected_args=["fake-tenant"])

    def test_flavor_fetch_extra_specs(self):
        self._verify("openstack.compute.v2.flavor.Flavor.fetch_extra_specs",
                     self.proxy.fetch_flavor_extra_specs,
                     method_args=["value"],
                     expected_args=[])

    def test_create_flavor_extra_specs(self):
        specs = {
            'a': 'b'
        }
        self._verify("openstack.compute.v2.flavor.Flavor.create_extra_specs",
                     self.proxy.create_flavor_extra_specs,
                     method_args=["value", specs],
                     expected_kwargs={"specs": specs})

    def test_get_flavor_extra_specs_prop(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.get_extra_specs_property",
            self.proxy.get_flavor_extra_specs_property,
            method_args=["value", "prop"],
            expected_args=["prop"])

    def test_update_flavor_extra_specs_prop(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.update_extra_specs_property",
            self.proxy.update_flavor_extra_specs_property,
            method_args=["value", "prop", "val"],
            expected_args=["prop", "val"])

    def test_delete_flavor_extra_specs_prop(self):
        self._verify(
            "openstack.compute.v2.flavor.Flavor.delete_extra_specs_property",
            self.proxy.delete_flavor_extra_specs_property,
            method_args=["value", "prop"],
            expected_args=["prop"])


class TestKeyPair(TestComputeProxy):
    def test_keypair_create(self):
        self.verify_create(self.proxy.create_keypair, keypair.Keypair)

    def test_keypair_delete(self):
        self.verify_delete(self.proxy.delete_keypair, keypair.Keypair, False)

    def test_keypair_delete_ignore(self):
        self.verify_delete(self.proxy.delete_keypair, keypair.Keypair, True)

    def test_keypair_delete_user_id(self):
        self.verify_delete(
            self.proxy.delete_keypair, keypair.Keypair,
            True,
            method_kwargs={'user_id': 'fake_user'},
            expected_kwargs={'user_id': 'fake_user'}
        )

    def test_keypair_find(self):
        self.verify_find(self.proxy.find_keypair, keypair.Keypair)

    def test_keypair_find_user_id(self):
        self.verify_find(
            self.proxy.find_keypair, keypair.Keypair,
            method_kwargs={'user_id': 'fake_user'},
            expected_kwargs={'user_id': 'fake_user'}
        )

    def test_keypair_get(self):
        self.verify_get(self.proxy.get_keypair, keypair.Keypair)

    def test_keypair_get_user_id(self):
        self.verify_get(
            self.proxy.get_keypair, keypair.Keypair,
            method_kwargs={'user_id': 'fake_user'},
            expected_kwargs={'user_id': 'fake_user'}
        )

    def test_keypairs(self):
        self.verify_list_no_kwargs(self.proxy.keypairs, keypair.Keypair)

    def test_keypairs_user_id(self):
        self.verify_list(
            self.proxy.keypairs, keypair.Keypair,
            method_kwargs={'user_id': 'fake_user'},
            expected_kwargs={'user_id': 'fake_user'}
        )


class TestAggregate(TestComputeProxy):
    def test_aggregate_create(self):
        self.verify_create(self.proxy.create_aggregate, aggregate.Aggregate)

    def test_aggregate_delete(self):
        self.verify_delete(
            self.proxy.delete_aggregate, aggregate.Aggregate, False)

    def test_aggregate_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_aggregate, aggregate.Aggregate, True)

    def test_aggregate_find(self):
        self.verify_find(self.proxy.find_aggregate, aggregate.Aggregate)

    def test_aggregates(self):
        self.verify_list_no_kwargs(self.proxy.aggregates, aggregate.Aggregate)

    def test_aggregate_get(self):
        self.verify_get(self.proxy.get_aggregate, aggregate.Aggregate)

    def test_aggregate_update(self):
        self.verify_update(self.proxy.update_aggregate, aggregate.Aggregate)

    def test_aggregate_add_host(self):
        self._verify("openstack.compute.v2.aggregate.Aggregate.add_host",
                     self.proxy.add_host_to_aggregate,
                     method_args=["value", "host"],
                     expected_args=["host"])

    def test_aggregate_remove_host(self):
        self._verify("openstack.compute.v2.aggregate.Aggregate.remove_host",
                     self.proxy.remove_host_from_aggregate,
                     method_args=["value", "host"],
                     expected_args=["host"])

    def test_aggregate_set_metadata(self):
        self._verify("openstack.compute.v2.aggregate.Aggregate.set_metadata",
                     self.proxy.set_aggregate_metadata,
                     method_args=["value", {'a': 'b'}],
                     expected_args=[{'a': 'b'}])

    def test_aggregate_precache_image(self):
        self._verify(
            "openstack.compute.v2.aggregate.Aggregate.precache_images",
            self.proxy.aggregate_precache_images,
            method_args=["value", '1'],
            expected_args=[[{'id': '1'}]])

    def test_aggregate_precache_images(self):
        self._verify(
            "openstack.compute.v2.aggregate.Aggregate.precache_images",
            self.proxy.aggregate_precache_images,
            method_args=["value", ['1', '2']],
            expected_args=[[{'id': '1'}, {'id': '2'}]])


class TestService(TestComputeProxy):
    def test_services(self):
        self.verify_list_no_kwargs(
            self.proxy.services, service.Service)

    @mock.patch('openstack.utils.supports_microversion', autospec=True,
                return_value=False)
    def test_enable_service_252(self, mv_mock):
        self._verify2(
            'openstack.compute.v2.service.Service.enable',
            self.proxy.enable_service,
            method_args=["value", "host1", "nova-compute"],
            expected_args=[self.proxy, "host1", "nova-compute"]
        )

    @mock.patch('openstack.utils.supports_microversion', autospec=True,
                return_value=True)
    def test_enable_service_253(self, mv_mock):
        self._verify2(
            'openstack.proxy.Proxy._update',
            self.proxy.enable_service,
            method_args=["value"],
            method_kwargs={},
            expected_args=[service.Service, "value"],
            expected_kwargs={'status': 'enabled'}
        )

    @mock.patch('openstack.utils.supports_microversion', autospec=True,
                return_value=False)
    def test_disable_service_252(self, mv_mock):
        self._verify2(
            'openstack.compute.v2.service.Service.disable',
            self.proxy.disable_service,
            method_args=["value", "host1", "nova-compute"],
            expected_args=[self.proxy, "host1", "nova-compute", None])

    @mock.patch('openstack.utils.supports_microversion', autospec=True,
                return_value=True)
    def test_disable_service_253(self, mv_mock):
        self._verify2(
            'openstack.proxy.Proxy._update',
            self.proxy.disable_service,
            method_args=["value"],
            method_kwargs={'disabled_reason': 'some_reason'},
            expected_args=[service.Service, "value"],
            expected_kwargs={
                'status': 'disabled',
                'disabled_reason': 'some_reason'
            }
        )

    @mock.patch('openstack.utils.supports_microversion', autospec=True,
                return_value=False)
    def test_force_service_down_252(self, mv_mock):
        self._verify2(
            'openstack.compute.v2.service.Service.set_forced_down',
            self.proxy.update_service_forced_down,
            method_args=["value", "host1", "nova-compute"],
            expected_args=[self.proxy, "host1", "nova-compute", True])

    @mock.patch('openstack.utils.supports_microversion', autospec=True,
                return_value=False)
    def test_force_service_down_252_empty_vals(self, mv_mock):
        self.assertRaises(
            ValueError,
            self.proxy.update_service_forced_down,
            "value", None, None
        )

    @mock.patch('openstack.utils.supports_microversion', autospec=True,
                return_value=False)
    def test_force_service_down_252_empty_vals_svc(self, mv_mock):
        self._verify2(
            'openstack.compute.v2.service.Service.set_forced_down',
            self.proxy.update_service_forced_down,
            method_args=[{'host': 'a', 'binary': 'b'}, None, None],
            expected_args=[self.proxy, None, None, True])

    def test_find_service(self):
        self.verify_find(
            self.proxy.find_service,
            service.Service,
        )

    def test_find_service_args(self):
        self.verify_find(
            self.proxy.find_service,
            service.Service,
            method_kwargs={'host': 'h1'},
            expected_kwargs={'host': 'h1'}
        )


class TestCompute(TestComputeProxy):
    def test_extension_find(self):
        self.verify_find(self.proxy.find_extension, extension.Extension)

    def test_extensions(self):
        self.verify_list_no_kwargs(self.proxy.extensions, extension.Extension)

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
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_images_not_detailed(self):
        self.verify_list(self.proxy.images, image.Image,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

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
        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.delete_server_interface,
                      method_args=[test_interface],
                      method_kwargs={"server": server_id},
                      expected_args=[server_interface.ServerInterface],
                      expected_kwargs={"server_id": server_id,
                                       "port_id": interface_id,
                                       "ignore_missing": True})

        # Case2: ServerInterface ID is provided as value
        self._verify2("openstack.proxy.Proxy._delete",
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
        self._verify2('openstack.proxy.Proxy._get',
                      self.proxy.get_server_interface,
                      method_args=[test_interface],
                      method_kwargs={"server": server_id},
                      expected_args=[server_interface.ServerInterface],
                      expected_kwargs={"port_id": interface_id,
                                       "server_id": server_id})

        # Case2: ServerInterface ID is provided as value
        self._verify2('openstack.proxy.Proxy._get',
                      self.proxy.get_server_interface,
                      method_args=[interface_id],
                      method_kwargs={"server": server_id},
                      expected_args=[server_interface.ServerInterface],
                      expected_kwargs={"port_id": interface_id,
                                       "server_id": server_id})

    def test_server_interfaces(self):
        self.verify_list(self.proxy.server_interfaces,
                         server_interface.ServerInterface,
                         method_args=["test_id"],
                         expected_kwargs={"server_id": "test_id"})

    def test_server_ips_with_network_label(self):
        self.verify_list(self.proxy.server_ips, server_ip.ServerIP,
                         method_args=["test_id"],
                         method_kwargs={"network_label": "test_label"},
                         expected_kwargs={"server_id": "test_id",
                                          "network_label": "test_label"})

    def test_server_ips_without_network_label(self):
        self.verify_list(self.proxy.server_ips, server_ip.ServerIP,
                         method_args=["test_id"],
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
        self.verify_list(self.proxy.servers, server.Server,
                         method_kwargs={"details": True,
                                        "changes_since": 1, "image": 2},
                         expected_kwargs={"changes_since": 1, "image": 2,
                                          "base_path": "/servers/detail"})

    def test_servers_not_detailed(self):
        self.verify_list(self.proxy.servers, server.Server,
                         method_kwargs={"details": False,
                                        "changes_since": 1, "image": 2},
                         expected_kwargs={"changes_since": 1, "image": 2})

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

    def test_availability_zones_not_detailed(self):
        self.verify_list(self.proxy.availability_zones,
                         az.AvailabilityZone,
                         method_kwargs={"details": False})

    def test_availability_zones_detailed(self):
        self.verify_list(self.proxy.availability_zones,
                         az.AvailabilityZoneDetail,
                         method_kwargs={"details": True})

    def test_get_all_server_metadata(self):
        self._verify2("openstack.compute.v2.server.Server.get_metadata",
                      self.proxy.get_server_metadata,
                      method_args=["value"],
                      method_result=server.Server(id="value", metadata={}),
                      expected_args=[self.proxy],
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
                      expected_args=[self.proxy],
                      expected_kwargs=kwargs,
                      expected_result=kwargs)

    def test_delete_server_metadata(self):
        self._verify2("openstack.compute.v2.server.Server.delete_metadata",
                      self.proxy.delete_server_metadata,
                      expected_result=None,
                      method_args=["value", "key"],
                      expected_args=[self.proxy, "key"])

    def test_create_image(self):
        metadata = {'k1': 'v1'}
        with mock.patch('openstack.compute.v2.server.Server.create_image') \
                as ci_mock:

            ci_mock.return_value = 'image_id'
            connection_mock = mock.Mock()
            connection_mock.get_image = mock.Mock(return_value='image')
            connection_mock.wait_for_image = mock.Mock()
            self.proxy._connection = connection_mock

            rsp = self.proxy.create_server_image(
                'server', 'image_name', metadata, wait=True, timeout=1)

            ci_mock.assert_called_with(
                self.proxy,
                'image_name',
                metadata
            )

            self.proxy._connection.get_image.assert_called_with('image_id')
            self.proxy._connection.wait_for_image.assert_called_with(
                'image',
                timeout=1)

            self.assertEqual(connection_mock.wait_for_image(), rsp)

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
        self.verify_list(self.proxy.server_groups, server_group.ServerGroup)

    def test_hypervisors_not_detailed(self):
        self.verify_list(self.proxy.hypervisors, hypervisor.Hypervisor,
                         method_kwargs={"details": False})

    def test_hypervisors_detailed(self):
        self.verify_list(self.proxy.hypervisors, hypervisor.HypervisorDetail,
                         method_kwargs={"details": True})

    def test_find_hypervisor(self):
        self.verify_find(self.proxy.find_hypervisor,
                         hypervisor.Hypervisor)

    def test_get_hypervisor(self):
        self.verify_get(self.proxy.get_hypervisor,
                        hypervisor.Hypervisor)

    def test_live_migrate_server(self):
        self._verify('openstack.compute.v2.server.Server.live_migrate',
                     self.proxy.live_migrate_server,
                     method_args=["value", "host1", False],
                     expected_args=["host1"],
                     expected_kwargs={'force': False, 'block_migration': None})

    def test_fetch_security_groups(self):
        self._verify(
            'openstack.compute.v2.server.Server.fetch_security_groups',
            self.proxy.fetch_server_security_groups,
            method_args=["value"],
            expected_args=[])

    def test_add_security_groups(self):
        self._verify(
            'openstack.compute.v2.server.Server.add_security_group',
            self.proxy.add_security_group_to_server,
            method_args=["value", {'id': 'id', 'name': 'sg'}],
            expected_args=['sg'])

    def test_remove_security_groups(self):
        self._verify(
            'openstack.compute.v2.server.Server.remove_security_group',
            self.proxy.remove_security_group_from_server,
            method_args=["value", {'id': 'id', 'name': 'sg'}],
            expected_args=['sg'])

    def test_create_server_remote_console(self):
        self.verify_create(
            self.proxy.create_server_remote_console,
            server_remote_console.ServerRemoteConsole,
            method_kwargs={"server": "test_id", "type": "fake"},
            expected_kwargs={"server_id": "test_id", "type": "fake"})

    def test_get_console_url(self):
        self._verify(
            'openstack.compute.v2.server.Server.get_console_url',
            self.proxy.get_server_console_url,
            method_args=["value", "console_type"],
            expected_args=["console_type"])

    @mock.patch('openstack.utils.supports_microversion', autospec=True)
    @mock.patch('openstack.compute.v2._proxy.Proxy._create', autospec=True)
    @mock.patch('openstack.compute.v2.server.Server.get_console_url',
                autospec=True)
    def test_create_console_mv_old(self, sgc, rcc, smv):
        console_fake = {
            'url': 'a',
            'type': 'b',
            'protocol': 'c'
        }
        smv.return_value = False
        sgc.return_value = console_fake
        ret = self.proxy.create_console('fake_server', 'fake_type')
        smv.assert_called_once_with(self.proxy, '2.6')
        rcc.assert_not_called()
        sgc.assert_called_with(mock.ANY, self.proxy, 'fake_type')
        self.assertDictEqual(console_fake, ret)

    @mock.patch('openstack.utils.supports_microversion', autospec=True)
    @mock.patch('openstack.compute.v2._proxy.Proxy._create', autospec=True)
    @mock.patch('openstack.compute.v2.server.Server.get_console_url',
                autospec=True)
    def test_create_console_mv_2_6(self, sgc, rcc, smv):
        console_fake = {
            'url': 'a',
            'type': 'b',
            'protocol': 'c'
        }

        # Test server_remote_console is triggered when mv>=2.6
        smv.return_value = True
        rcc.return_value = server_remote_console.ServerRemoteConsole(
            **console_fake)
        ret = self.proxy.create_console('fake_server', 'fake_type')
        smv.assert_called_once_with(self.proxy, '2.6')
        sgc.assert_not_called()
        rcc.assert_called_with(mock.ANY,
                               server_remote_console.ServerRemoteConsole,
                               server_id='fake_server',
                               type='fake_type',
                               protocol=None)
        self.assertEqual(console_fake['url'], ret['url'])
