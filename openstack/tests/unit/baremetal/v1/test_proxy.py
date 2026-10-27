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

from typing import Any
from unittest import mock

from openstack.baremetal.v1 import _proxy
from openstack.baremetal.v1 import allocation
from openstack.baremetal.v1 import chassis
from openstack.baremetal.v1 import conductor
from openstack.baremetal.v1 import deploy_templates
from openstack.baremetal.v1 import driver
from openstack.baremetal.v1 import inspection_rules
from openstack.baremetal.v1 import node
from openstack.baremetal.v1 import port
from openstack.baremetal.v1 import port_group
from openstack.baremetal.v1 import runbooks
from openstack.baremetal.v1 import volume_connector
from openstack.baremetal.v1 import volume_target
from openstack import exceptions
from openstack.tests.unit import base
from openstack.tests.unit import test_proxy_base


_MOCK_METHOD = 'openstack.baremetal.v1._proxy.Proxy._get_with_fields'
_PATCH = [{'op': 'add', 'path': '/extra/foo', 'value': 'bar'}]


class TestBaremetalProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestPatch(TestBaremetalProxy):
    def test_patch(self):
        for method, resource_type in (
            (self.proxy.patch_chassis, chassis.Chassis),
            (self.proxy.patch_port, port.Port),
            (self.proxy.patch_port_group, port_group.PortGroup),
            (self.proxy.patch_allocation, allocation.Allocation),
            (
                self.proxy.patch_volume_connector,
                volume_connector.VolumeConnector,
            ),
            (self.proxy.patch_volume_target, volume_target.VolumeTarget),
            (
                self.proxy.patch_deploy_template,
                deploy_templates.DeployTemplate,
            ),
            (self.proxy.patch_runbook, runbooks.Runbook),
            (
                self.proxy.patch_inspection_rule,
                inspection_rules.InspectionRule,
            ),
        ):
            with self.subTest(method=method.__name__):
                self._verify(
                    'openstack.proxy.Proxy._patch',
                    method,
                    method_args=['resource_id', _PATCH],
                    expected_args=[resource_type, 'resource_id', _PATCH],
                    expected_result='result',
                )


class TestDrivers(TestBaremetalProxy):
    def test_drivers(self):
        self.verify_list(self.proxy.drivers, driver.Driver)

    @mock.patch.object(driver.Driver, 'list')
    def test_drivers_detailed(self, mock_list):
        result = self.proxy.drivers(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=True, query=1
        )

    def test_get_driver(self):
        self.verify_get(self.proxy.get_driver, driver.Driver)

    @mock.patch.object(_proxy.Proxy, 'get_driver', autospec=True)
    def test_list_driver_vendor_passthru(self, mock_get):
        result = self.proxy.list_driver_vendor_passthru('ipmi')
        mock_get.assert_called_once_with(self.proxy, 'ipmi')
        mock_list = mock_get.return_value.list_vendor_passthru
        mock_list.assert_called_once_with(self.proxy)
        self.assertIs(result, mock_list.return_value)

    @mock.patch.object(_proxy.Proxy, 'get_driver', autospec=True)
    def test_call_driver_vendor_passthru(self, mock_get):
        result = self.proxy.call_driver_vendor_passthru(
            'ipmi', 'POST', 'do_it', {'a': 'b'}
        )
        mock_get.assert_called_once_with(self.proxy, 'ipmi')
        mock_call = mock_get.return_value.call_vendor_passthru
        mock_call.assert_called_once_with(
            self.proxy, 'POST', 'do_it', {'a': 'b'}
        )
        self.assertIs(result, mock_call.return_value)


class TestChassis(TestBaremetalProxy):
    @mock.patch.object(chassis.Chassis, 'list')
    def test_chassis_detailed(self, mock_list):
        result = self.proxy.chassis(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=True, query=1
        )

    @mock.patch.object(chassis.Chassis, 'list')
    def test_chassis_not_detailed(self, mock_list):
        result = self.proxy.chassis(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=False, query=1
        )

    def test_create_chassis(self):
        self.verify_create(self.proxy.create_chassis, chassis.Chassis)

    def test_find_chassis(self):
        self.verify_find(
            self.proxy.find_chassis,
            chassis.Chassis,
            expected_kwargs={'details': True},
        )

    def test_get_chassis(self):
        self.verify_get(
            self.proxy.get_chassis,
            chassis.Chassis,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_chassis(self):
        self.verify_update(self.proxy.update_chassis, chassis.Chassis)

    def test_delete_chassis(self):
        self.verify_delete(self.proxy.delete_chassis, chassis.Chassis, False)

    def test_delete_chassis_ignore(self):
        self.verify_delete(self.proxy.delete_chassis, chassis.Chassis, True)


class TestNode(TestBaremetalProxy):
    @mock.patch.object(node.Node, 'list')
    def test_nodes_detailed(self, mock_list):
        result = self.proxy.nodes(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=True, query=1
        )

    @mock.patch.object(node.Node, 'list')
    def test_nodes_not_detailed(self, mock_list):
        result = self.proxy.nodes(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=False, query=1
        )

    @mock.patch.object(node.Node, 'list')
    def test_nodes_sharded(self, mock_list):
        kwargs: dict[str, Any] = {"shard": 'meow', "query": 1}
        result = self.proxy.nodes(fields=("uuid", "instance_uuid"), **kwargs)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy,
            paginated=True,
            base_path=None,
            details=False,
            fields=('uuid', 'instance_uuid'),
            shard='meow',
            query=1,
        )

    def test_create_node(self):
        self.verify_create(self.proxy.create_node, node.Node)

    def test_find_node(self):
        self.verify_find(
            self.proxy.find_node,
            node.Node,
            expected_kwargs={'details': True},
        )

    def test_get_node(self):
        self.verify_get(
            self.proxy.get_node,
            node.Node,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    @mock.patch.object(node.Node, 'commit', autospec=True)
    def test_update_node(self, mock_commit):
        self.proxy.update_node('uuid', instance_id='new value')
        mock_commit.assert_called_once_with(
            mock.ANY, self.proxy, retry_on_conflict=True
        )
        self.assertEqual('new value', mock_commit.call_args[0][0].instance_id)

    @mock.patch.object(node.Node, 'commit', autospec=True)
    def test_update_node_no_retries(self, mock_commit):
        self.proxy.update_node(
            'uuid', instance_id='new value', retry_on_conflict=False
        )
        mock_commit.assert_called_once_with(
            mock.ANY, self.proxy, retry_on_conflict=False
        )
        self.assertEqual('new value', mock_commit.call_args[0][0].instance_id)

    def test_delete_node(self):
        self.verify_delete(self.proxy.delete_node, node.Node, False)

    def test_delete_node_ignore(self):
        self.verify_delete(self.proxy.delete_node, node.Node, True)

    @mock.patch.object(node.Node, 'patch', autospec=True)
    def test_patch_node(self, mock_patch):
        result = self.proxy.patch_node('uuid', _PATCH)
        self.assertIs(result, mock_patch.return_value)
        mock_patch.assert_called_once_with(
            mock.ANY,
            self.proxy,
            _PATCH,
            retry_on_conflict=True,
            reset_interfaces=None,
        )
        self.assertEqual('uuid', mock_patch.call_args[0][0].id)

    @mock.patch.object(node.Node, 'patch', autospec=True)
    def test_patch_node_reset_interfaces_no_retries(self, mock_patch):
        self.proxy.patch_node(
            'uuid', _PATCH, reset_interfaces=True, retry_on_conflict=False
        )
        mock_patch.assert_called_once_with(
            mock.ANY,
            self.proxy,
            _PATCH,
            retry_on_conflict=False,
            reset_interfaces=True,
        )

    @mock.patch.object(node.Node, 'get_node_inventory', autospec=True)
    def test_get_node_inventory(self, mock_inventory):
        result = self.proxy.get_node_inventory('uuid')
        self.assertIs(result, mock_inventory.return_value)
        mock_inventory.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_inventory.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_provision_state', autospec=True)
    def test_set_node_provision_state(self, mock_set):
        result = self.proxy.set_node_provision_state('uuid', 'provide')
        self.assertIs(result, mock_set.return_value)
        mock_set.assert_called_once_with(
            mock.ANY,
            self.proxy,
            'provide',
            config_drive=None,
            clean_steps=None,
            rescue_password=None,
            wait=False,
            timeout=None,
            deploy_steps=None,
        )
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_provision_state', autospec=True)
    def test_set_node_provision_state_all_args(self, mock_set):
        steps = [{'interface': 'deploy', 'step': 'foo', 'priority': 10}]
        self.proxy.set_node_provision_state(
            'uuid',
            'active',
            config_drive='abcd',
            wait=True,
            timeout=42,
            deploy_steps=steps,
        )
        mock_set.assert_called_once_with(
            mock.ANY,
            self.proxy,
            'active',
            config_drive='abcd',
            clean_steps=None,
            rescue_password=None,
            wait=True,
            timeout=42,
            deploy_steps=steps,
        )

    @mock.patch.object(node.Node, 'get_boot_device', autospec=True)
    def test_get_node_boot_device(self, mock_get):
        result = self.proxy.get_node_boot_device('uuid')
        self.assertIs(result, mock_get.return_value)
        mock_get.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_get.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_boot_device', autospec=True)
    def test_set_node_boot_device(self, mock_set):
        self.proxy.set_node_boot_device('uuid', 'pxe')
        mock_set.assert_called_once_with(
            mock.ANY, self.proxy, 'pxe', persistent=False
        )
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_boot_device', autospec=True)
    def test_set_node_boot_device_persistent(self, mock_set):
        self.proxy.set_node_boot_device('uuid', 'disk', persistent=True)
        mock_set.assert_called_once_with(
            mock.ANY, self.proxy, 'disk', persistent=True
        )

    @mock.patch.object(node.Node, 'get_supported_boot_devices', autospec=True)
    def test_get_node_supported_boot_devices(self, mock_get):
        result = self.proxy.get_node_supported_boot_devices('uuid')
        self.assertIs(result, mock_get.return_value)
        mock_get.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_get.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_boot_mode', autospec=True)
    def test_set_node_boot_mode(self, mock_set):
        self.proxy.set_node_boot_mode('uuid', 'uefi')
        mock_set.assert_called_once_with(mock.ANY, self.proxy, 'uefi')
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_secure_boot', autospec=True)
    def test_set_node_secure_boot(self, mock_set):
        self.proxy.set_node_secure_boot('uuid', True)
        mock_set.assert_called_once_with(mock.ANY, self.proxy, True)
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'inject_nmi', autospec=True)
    def test_inject_nmi_to_node(self, mock_nmi):
        self.proxy.inject_nmi_to_node('uuid')
        mock_nmi.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_nmi.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_power_state', autospec=True)
    def test_set_node_power_state(self, mock_set):
        self.proxy.set_node_power_state('uuid', 'power on')
        mock_set.assert_called_once_with(
            mock.ANY, self.proxy, 'power on', wait=False, timeout=None
        )
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_power_state', autospec=True)
    def test_set_node_power_state_wait(self, mock_set):
        self.proxy.set_node_power_state(
            'uuid', node.PowerAction.REBOOT, wait=True, timeout=42
        )
        mock_set.assert_called_once_with(
            mock.ANY,
            self.proxy,
            node.PowerAction.REBOOT,
            wait=True,
            timeout=42,
        )

    @mock.patch.object(node.Node, 'wait_for_power_state', autospec=True)
    def test_wait_for_node_power_state(self, mock_wait):
        result = self.proxy.wait_for_node_power_state(
            'uuid', 'power off', timeout=42
        )
        self.assertIs(result, mock_wait.return_value)
        mock_wait.assert_called_once_with(
            mock.ANY, self.proxy, 'power off', timeout=42
        )
        self.assertEqual('uuid', mock_wait.call_args[0][0].id)

    @mock.patch.object(node.Node, 'wait_for_reservation', autospec=True)
    def test_wait_for_node_reservation(self, mock_wait):
        result = self.proxy.wait_for_node_reservation('uuid', timeout=42)
        self.assertIs(result, mock_wait.return_value)
        mock_wait.assert_called_once_with(mock.ANY, self.proxy, timeout=42)
        self.assertEqual('uuid', mock_wait.call_args[0][0].id)

    @mock.patch.object(node.Node, 'validate', autospec=True)
    def test_validate_node(self, mock_validate):
        result = self.proxy.validate_node('uuid')
        self.assertIs(result, mock_validate.return_value)
        mock_validate.assert_called_once_with(
            mock.ANY, self.proxy, required=('boot', 'deploy', 'power')
        )
        self.assertEqual('uuid', mock_validate.call_args[0][0].id)

    @mock.patch.object(node.Node, 'validate', autospec=True)
    def test_validate_node_required(self, mock_validate):
        self.proxy.validate_node('uuid', required=['power'])
        mock_validate.assert_called_once_with(
            mock.ANY, self.proxy, required=['power']
        )

    @mock.patch.object(node.Node, 'set_maintenance', autospec=True)
    def test_set_node_maintenance(self, mock_set):
        result = self.proxy.set_node_maintenance('uuid', 'broken')
        self.assertIs(result, mock_set.return_value)
        mock_set.assert_called_once_with(mock.ANY, self.proxy, 'broken')
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_maintenance', autospec=True)
    def test_set_node_maintenance_no_reason(self, mock_set):
        self.proxy.set_node_maintenance('uuid')
        mock_set.assert_called_once_with(mock.ANY, self.proxy, None)

    @mock.patch.object(node.Node, 'unset_maintenance', autospec=True)
    def test_unset_node_maintenance(self, mock_unset):
        result = self.proxy.unset_node_maintenance('uuid')
        self.assertIs(result, mock_unset.return_value)
        mock_unset.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_unset.call_args[0][0].id)

    @mock.patch.object(node.Node, 'add_trait', autospec=True)
    def test_add_node_trait(self, mock_add):
        self.proxy.add_node_trait('uuid', 'CUSTOM_FOO')
        mock_add.assert_called_once_with(mock.ANY, self.proxy, 'CUSTOM_FOO')
        self.assertEqual('uuid', mock_add.call_args[0][0].id)

    @mock.patch.object(node.Node, 'remove_trait', autospec=True)
    def test_remove_node_trait(self, mock_remove):
        result = self.proxy.remove_node_trait('uuid', 'CUSTOM_FOO')
        self.assertIs(result, mock_remove.return_value)
        mock_remove.assert_called_once_with(
            mock.ANY, self.proxy, 'CUSTOM_FOO', ignore_missing=True
        )
        self.assertEqual('uuid', mock_remove.call_args[0][0].id)

    @mock.patch.object(node.Node, 'remove_trait', autospec=True)
    def test_remove_node_trait_not_ignore_missing(self, mock_remove):
        self.proxy.remove_node_trait(
            'uuid', 'CUSTOM_FOO', ignore_missing=False
        )
        mock_remove.assert_called_once_with(
            mock.ANY, self.proxy, 'CUSTOM_FOO', ignore_missing=False
        )

    @mock.patch.object(node.Node, 'set_traits', autospec=True)
    def test_set_node_traits(self, mock_set):
        self.proxy.set_node_traits('uuid', ['CUSTOM_FOO', 'CUSTOM_BAR'])
        mock_set.assert_called_once_with(
            mock.ANY, self.proxy, ['CUSTOM_FOO', 'CUSTOM_BAR']
        )
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'call_vendor_passthru', autospec=True)
    def test_call_node_vendor_passthru(self, mock_call):
        result = self.proxy.call_node_vendor_passthru(
            'uuid', 'POST', 'do_it', {'a': 'b'}
        )
        self.assertIs(result, mock_call.return_value)
        mock_call.assert_called_once_with(
            mock.ANY, self.proxy, 'POST', 'do_it', {'a': 'b'}
        )
        self.assertEqual('uuid', mock_call.call_args[0][0].id)

    @mock.patch.object(node.Node, 'list_vendor_passthru', autospec=True)
    def test_list_node_vendor_passthru(self, mock_list):
        result = self.proxy.list_node_vendor_passthru('uuid')
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_list.call_args[0][0].id)

    @mock.patch.object(node.Node, 'get_console', autospec=True)
    def test_get_node_console(self, mock_get):
        result = self.proxy.get_node_console('uuid')
        self.assertIs(result, mock_get.return_value)
        mock_get.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_get.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_console_mode', autospec=True)
    def test_enable_node_console(self, mock_set):
        self.proxy.enable_node_console('uuid')
        mock_set.assert_called_once_with(mock.ANY, self.proxy, True)
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'set_console_mode', autospec=True)
    def test_disable_node_console(self, mock_set):
        self.proxy.disable_node_console('uuid')
        mock_set.assert_called_once_with(mock.ANY, self.proxy, False)
        self.assertEqual('uuid', mock_set.call_args[0][0].id)

    @mock.patch.object(node.Node, 'list_firmware', autospec=True)
    def test_list_node_firmware(self, mock_list):
        result = self.proxy.list_node_firmware('uuid')
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_list.call_args[0][0].id)

    @mock.patch.object(node.Node, 'attach_vmedia', autospec=True)
    def test_attach_vmedia_to_node(self, mock_attach):
        self.proxy.attach_vmedia_to_node(
            'uuid', 'cdrom', 'http://example.com/image.iso'
        )
        mock_attach.assert_called_once_with(
            mock.ANY,
            self.proxy,
            device_type='cdrom',
            image_url='http://example.com/image.iso',
            image_download_source=None,
            retry_on_conflict=True,
        )
        self.assertEqual('uuid', mock_attach.call_args[0][0].id)

    @mock.patch.object(node.Node, 'attach_vmedia', autospec=True)
    def test_attach_vmedia_to_node_all_args(self, mock_attach):
        self.proxy.attach_vmedia_to_node(
            'uuid',
            'cdrom',
            'http://example.com/image.iso',
            image_download_source='http',
            retry_on_conflict=False,
        )
        mock_attach.assert_called_once_with(
            mock.ANY,
            self.proxy,
            device_type='cdrom',
            image_url='http://example.com/image.iso',
            image_download_source='http',
            retry_on_conflict=False,
        )

    @mock.patch.object(node.Node, 'detach_vmedia', autospec=True)
    def test_detach_vmedia_from_node(self, mock_detach):
        self.proxy.detach_vmedia_from_node('uuid')
        mock_detach.assert_called_once_with(
            mock.ANY, self.proxy, device_types=None
        )
        self.assertEqual('uuid', mock_detach.call_args[0][0].id)

    @mock.patch.object(node.Node, 'detach_vmedia', autospec=True)
    def test_detach_vmedia_from_node_device_types(self, mock_detach):
        self.proxy.detach_vmedia_from_node('uuid', device_types=['cdrom'])
        mock_detach.assert_called_once_with(
            mock.ANY, self.proxy, device_types=['cdrom']
        )

    @mock.patch.object(node.Node, 'attach_vif', autospec=True)
    def test_attach_vif_to_node(self, mock_attach):
        self.proxy.attach_vif_to_node('uuid', 'vif-id')
        mock_attach.assert_called_once_with(
            mock.ANY,
            self.proxy,
            vif_id='vif-id',
            retry_on_conflict=True,
            port_id=None,
            port_group_id=None,
        )
        self.assertEqual('uuid', mock_attach.call_args[0][0].id)

    @mock.patch.object(node.Node, 'attach_vif', autospec=True)
    def test_attach_vif_to_node_with_port(self, mock_attach):
        self.proxy.attach_vif_to_node(
            'uuid',
            'vif-id',
            retry_on_conflict=False,
            port=port.Port(id='port-id'),
        )
        mock_attach.assert_called_once_with(
            mock.ANY,
            self.proxy,
            vif_id='vif-id',
            retry_on_conflict=False,
            port_id='port-id',
            port_group_id=None,
        )

    @mock.patch.object(node.Node, 'attach_vif', autospec=True)
    def test_attach_vif_to_node_with_port_group(self, mock_attach):
        self.proxy.attach_vif_to_node(
            'uuid', 'vif-id', port_group='port-group-id'
        )
        mock_attach.assert_called_once_with(
            mock.ANY,
            self.proxy,
            vif_id='vif-id',
            retry_on_conflict=True,
            port_id=None,
            port_group_id='port-group-id',
        )

    @mock.patch.object(node.Node, 'detach_vif', autospec=True)
    def test_detach_vif_from_node(self, mock_detach):
        result = self.proxy.detach_vif_from_node('uuid', 'vif-id')
        self.assertIs(result, mock_detach.return_value)
        mock_detach.assert_called_once_with(
            mock.ANY, self.proxy, 'vif-id', ignore_missing=True
        )
        self.assertEqual('uuid', mock_detach.call_args[0][0].id)

    @mock.patch.object(node.Node, 'detach_vif', autospec=True)
    def test_detach_vif_from_node_not_ignore_missing(self, mock_detach):
        self.proxy.detach_vif_from_node('uuid', 'vif-id', ignore_missing=False)
        mock_detach.assert_called_once_with(
            mock.ANY, self.proxy, 'vif-id', ignore_missing=False
        )

    @mock.patch.object(node.Node, 'list_vifs', autospec=True)
    def test_list_node_vifs(self, mock_list):
        result = self.proxy.list_node_vifs('uuid')
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(mock.ANY, self.proxy)
        self.assertEqual('uuid', mock_list.call_args[0][0].id)


class TestPort(TestBaremetalProxy):
    @mock.patch.object(port.Port, 'list')
    def test_ports_detailed(self, mock_list):
        result = self.proxy.ports(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=True, query=1
        )

    @mock.patch.object(port.Port, 'list')
    def test_ports_not_detailed(self, mock_list):
        result = self.proxy.ports(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=False, query=1
        )

    def test_create_port(self):
        self.verify_create(self.proxy.create_port, port.Port)

    def test_find_port(self):
        self.verify_find(
            self.proxy.find_port,
            port.Port,
            expected_kwargs={'details': True},
        )

    def test_get_port(self):
        self.verify_get(
            self.proxy.get_port,
            port.Port,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_port(self):
        self.verify_update(self.proxy.update_port, port.Port)

    def test_delete_port(self):
        self.verify_delete(self.proxy.delete_port, port.Port, False)

    def test_delete_port_ignore(self):
        self.verify_delete(self.proxy.delete_port, port.Port, True)


class TestPortGroups(TestBaremetalProxy):
    @mock.patch.object(port_group.PortGroup, 'list')
    def test_port_groups_detailed(self, mock_list):
        result = self.proxy.port_groups(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=True, query=1
        )

    @mock.patch.object(port_group.PortGroup, 'list')
    def test_port_groups_not_detailed(self, mock_list):
        result = self.proxy.port_groups(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=False, query=1
        )

    def test_create_port_group(self):
        self.verify_create(self.proxy.create_port_group, port_group.PortGroup)

    def test_find_port_group(self):
        self.verify_find(
            self.proxy.find_port_group,
            port_group.PortGroup,
            expected_kwargs={'details': True},
        )

    def test_get_port_group(self):
        self.verify_get(
            self.proxy.get_port_group,
            port_group.PortGroup,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_port_group(self):
        self.verify_update(self.proxy.update_port_group, port_group.PortGroup)

    def test_delete_port_group(self):
        self.verify_delete(
            self.proxy.delete_port_group, port_group.PortGroup, False
        )

    def test_delete_port_group_ignore(self):
        self.verify_delete(
            self.proxy.delete_port_group, port_group.PortGroup, True
        )


class TestAllocation(TestBaremetalProxy):
    def test_allocations(self):
        self.verify_list(self.proxy.allocations, allocation.Allocation)

    def test_create_allocation(self):
        self.verify_create(self.proxy.create_allocation, allocation.Allocation)

    def test_update_allocation(self):
        self.verify_update(self.proxy.update_allocation, allocation.Allocation)

    @mock.patch.object(allocation.Allocation, 'wait', autospec=True)
    def test_wait_for_allocation(self, mock_wait):
        result = self.proxy.wait_for_allocation('uuid')
        self.assertIs(result, mock_wait.return_value)
        mock_wait.assert_called_once_with(
            mock.ANY, self.proxy, timeout=None, ignore_error=False
        )
        self.assertEqual('uuid', mock_wait.call_args[0][0].id)

    @mock.patch.object(allocation.Allocation, 'wait', autospec=True)
    def test_wait_for_allocation_all_args(self, mock_wait):
        self.proxy.wait_for_allocation('uuid', timeout=42, ignore_error=True)
        mock_wait.assert_called_once_with(
            mock.ANY, self.proxy, timeout=42, ignore_error=True
        )

    def test_get_allocation(self):
        self.verify_get(
            self.proxy.get_allocation,
            allocation.Allocation,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_delete_allocation(self):
        self.verify_delete(
            self.proxy.delete_allocation, allocation.Allocation, False
        )

    def test_delete_allocation_ignore(self):
        self.verify_delete(
            self.proxy.delete_allocation, allocation.Allocation, True
        )


class TestVolumeConnector(TestBaremetalProxy):
    @mock.patch.object(volume_connector.VolumeConnector, 'list')
    def test_volume_connector_detailed(self, mock_list):
        result = self.proxy.volume_connectors(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, detail=True, query=1
        )

    @mock.patch.object(volume_connector.VolumeConnector, 'list')
    def test_volume_connector_not_detailed(self, mock_list):
        result = self.proxy.volume_connectors(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, query=1
        )

    def test_create_volume_connector(self):
        self.verify_create(
            self.proxy.create_volume_connector,
            volume_connector.VolumeConnector,
        )

    def test_find_volume_connector(self):
        self.verify_find(
            self.proxy.find_volume_connector,
            volume_connector.VolumeConnector,
            expected_kwargs={'details': True},
        )

    def test_get_volume_connector(self):
        self.verify_get(
            self.proxy.get_volume_connector,
            volume_connector.VolumeConnector,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_volume_connector(self):
        self.verify_update(
            self.proxy.update_volume_connector,
            volume_connector.VolumeConnector,
        )

    def test_delete_volume_connector(self):
        self.verify_delete(
            self.proxy.delete_volume_connector,
            volume_connector.VolumeConnector,
            False,
        )

    def test_delete_volume_connector_ignore(self):
        self.verify_delete(
            self.proxy.delete_volume_connector,
            volume_connector.VolumeConnector,
            True,
        )


class TestVolumeTarget(TestBaremetalProxy):
    @mock.patch.object(volume_target.VolumeTarget, 'list')
    def test_volume_target_detailed(self, mock_list):
        result = self.proxy.volume_targets(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, detail=True, query=1
        )

    @mock.patch.object(volume_target.VolumeTarget, 'list')
    def test_volume_target_not_detailed(self, mock_list):
        result = self.proxy.volume_targets(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, query=1
        )

    def test_create_volume_target(self):
        self.verify_create(
            self.proxy.create_volume_target, volume_target.VolumeTarget
        )

    def test_find_volume_target(self):
        self.verify_find(
            self.proxy.find_volume_target,
            volume_target.VolumeTarget,
            expected_kwargs={'details': True},
        )

    def test_get_volume_target(self):
        self.verify_get(
            self.proxy.get_volume_target,
            volume_target.VolumeTarget,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_volume_target(self):
        self.verify_update(
            self.proxy.update_volume_target, volume_target.VolumeTarget
        )

    def test_delete_volume_target(self):
        self.verify_delete(
            self.proxy.delete_volume_target, volume_target.VolumeTarget, False
        )

    def test_delete_volume_target_ignore(self):
        self.verify_delete(
            self.proxy.delete_volume_target, volume_target.VolumeTarget, True
        )


class TestDeployTemplate(TestBaremetalProxy):
    @mock.patch.object(deploy_templates.DeployTemplate, 'list')
    def test_deploy_templates_detailed(self, mock_list):
        result = self.proxy.deploy_templates(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, detail=True, query=1
        )

    @mock.patch.object(deploy_templates.DeployTemplate, 'list')
    def test_deploy_templates_not_detailed(self, mock_list):
        result = self.proxy.deploy_templates(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, query=1
        )

    def test_create_deploy_template(self):
        self.verify_create(
            self.proxy.create_deploy_template,
            deploy_templates.DeployTemplate,
        )

    def test_find_deploy_template(self):
        self.verify_find(
            self.proxy.find_deploy_template,
            deploy_templates.DeployTemplate,
            expected_kwargs={'details': True},
        )

    def test_get_deploy_template(self):
        self.verify_get(
            self.proxy.get_deploy_template,
            deploy_templates.DeployTemplate,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_deploy_template(self):
        self.verify_update(
            self.proxy.update_deploy_template,
            deploy_templates.DeployTemplate,
        )

    def test_delete_deploy_template(self):
        self.verify_delete(
            self.proxy.delete_deploy_template,
            deploy_templates.DeployTemplate,
            False,
        )

    def test_delete_deploy_template_ignore(self):
        self.verify_delete(
            self.proxy.delete_deploy_template,
            deploy_templates.DeployTemplate,
            True,
        )


class TestRunbook(TestBaremetalProxy):
    @mock.patch.object(runbooks.Runbook, 'list')
    def test_runbooks_detailed(self, mock_list):
        result = self.proxy.runbooks(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, detail=True, query=1
        )

    @mock.patch.object(runbooks.Runbook, 'list')
    def test_runbooks_not_detailed(self, mock_list):
        result = self.proxy.runbooks(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, query=1
        )

    def test_create_runbook(self):
        self.verify_create(self.proxy.create_runbook, runbooks.Runbook)

    def test_get_runbook(self):
        self.verify_get(
            self.proxy.get_runbook,
            runbooks.Runbook,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_runbook(self):
        self.verify_update(self.proxy.update_runbook, runbooks.Runbook)

    def test_delete_runbook(self):
        self.verify_delete(self.proxy.delete_runbook, runbooks.Runbook, False)

    def test_delete_runbook_ignore(self):
        self.verify_delete(self.proxy.delete_runbook, runbooks.Runbook, True)

    @mock.patch.object(runbooks.Runbook, 'add_trait', autospec=True)
    def test_add_runbook_trait(self, mock_add):
        self.proxy.add_runbook_trait('uuid', 'CUSTOM_FOO')
        mock_add.assert_called_once_with(mock.ANY, self.proxy, 'CUSTOM_FOO')
        self.assertEqual('uuid', mock_add.call_args[0][0].id)

    @mock.patch.object(runbooks.Runbook, 'remove_trait', autospec=True)
    def test_remove_runbook_trait(self, mock_remove):
        self.proxy.remove_runbook_trait('uuid', 'CUSTOM_FOO')
        mock_remove.assert_called_once_with(mock.ANY, self.proxy, 'CUSTOM_FOO')
        self.assertEqual('uuid', mock_remove.call_args[0][0].id)

    @mock.patch.object(runbooks.Runbook, 'set_traits', autospec=True)
    def test_set_runbook_traits(self, mock_set):
        self.proxy.set_runbook_traits('uuid', ['CUSTOM_FOO', 'CUSTOM_BAR'])
        mock_set.assert_called_once_with(
            mock.ANY, self.proxy, ['CUSTOM_FOO', 'CUSTOM_BAR']
        )
        self.assertEqual('uuid', mock_set.call_args[0][0].id)


class TestConductor(TestBaremetalProxy):
    @mock.patch.object(conductor.Conductor, 'list')
    def test_conductors_detailed(self, mock_list):
        result = self.proxy.conductors(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=True, query=1
        )

    @mock.patch.object(conductor.Conductor, 'list')
    def test_conductors_not_detailed(self, mock_list):
        result = self.proxy.conductors(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, query=1
        )

    def test_get_conductor(self):
        self.verify_get(
            self.proxy.get_conductor,
            conductor.Conductor,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )


class TestWait(TestBaremetalProxy):
    def test_wait_for_status(self):
        value = node.Node(id='uuid')
        self.verify_wait_for_status(
            self.proxy.wait_for_status,
            method_args=[value, 'active'],
            expected_args=[
                self.proxy,
                value,
                'active',
                None,
                2,
                None,
                'status',
                None,
            ],
        )

    def test_wait_for_delete(self):
        value = node.Node(id='uuid')
        self.verify_wait_for_status(
            self.proxy.wait_for_delete,
            mock_method='openstack.resource.wait_for_delete',
            method_args=[value],
            expected_args=[self.proxy, value, 2, 120, None],
        )


class TestMisc(TestBaremetalProxy):
    @mock.patch.object(node.Node, 'fetch', autospec=True)
    def test__get_with_fields_none(self, mock_fetch):
        result = self.proxy._get_with_fields(node.Node, 'value')
        self.assertIs(result, mock_fetch.return_value)
        mock_fetch.assert_called_once_with(
            mock.ANY, self.proxy, error_message=mock.ANY
        )

    @mock.patch.object(node.Node, 'fetch', autospec=True)
    def test__get_with_fields_node(self, mock_fetch):
        result = self.proxy._get_with_fields(
            # Mix of server-side and client-side fields
            node.Node,
            'value',
            fields=['maintenance', 'id', 'instance_id'],
        )
        self.assertIs(result, mock_fetch.return_value)
        mock_fetch.assert_called_once_with(
            mock.ANY,
            self.proxy,
            error_message=mock.ANY,
            # instance_id converted to server-side instance_uuid
            fields='maintenance,uuid,instance_uuid',
        )

    @mock.patch.object(port.Port, 'fetch', autospec=True)
    def test__get_with_fields_port(self, mock_fetch):
        result = self.proxy._get_with_fields(
            port.Port, 'value', fields=['address', 'id', 'node_id']
        )
        self.assertIs(result, mock_fetch.return_value)
        mock_fetch.assert_called_once_with(
            mock.ANY,
            self.proxy,
            error_message=mock.ANY,
            # node_id converted to server-side node_uuid
            fields='address,uuid,node_uuid',
        )


@mock.patch('time.sleep', lambda _sec: None)
@mock.patch.object(_proxy.Proxy, 'get_node', autospec=True)
class TestWaitForNodesProvisionState(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock()
        self.proxy = _proxy.Proxy(self.session)

    def test_success(self, mock_get):
        # two attempts, one node succeeds after the 1st
        nodes = [mock.Mock(spec=node.Node, id=str(i)) for i in range(3)]
        for i, n in enumerate(nodes):
            # 1st attempt on 1st node, 2nd attempt on 2nd node
            n._check_state_reached.return_value = not (i % 2)
            mock_get.side_effect = nodes

        result = self.proxy.wait_for_nodes_provision_state(
            ['abcd', node.Node(id='1234')], 'fake state'
        )
        self.assertEqual([nodes[0], nodes[2]], result)

        for n in nodes:
            n._check_state_reached.assert_called_once_with(
                self.proxy, 'fake state', True
            )

    def test_success_no_fail(self, mock_get):
        # two attempts, one node succeeds after the 1st
        nodes = [mock.Mock(spec=node.Node, id=str(i)) for i in range(3)]
        for i, n in enumerate(nodes):
            # 1st attempt on 1st node, 2nd attempt on 2nd node
            n._check_state_reached.return_value = not (i % 2)
            mock_get.side_effect = nodes

        result = self.proxy.wait_for_nodes_provision_state(
            ['abcd', node.Node(id='1234')], 'fake state', fail=False
        )
        self.assertEqual([nodes[0], nodes[2]], result.success)
        self.assertEqual([], result.failure)
        self.assertEqual([], result.timeout)

        for n in nodes:
            n._check_state_reached.assert_called_once_with(
                self.proxy, 'fake state', True
            )

    def test_timeout(self, mock_get):
        mock_get.return_value._check_state_reached.return_value = False
        mock_get.return_value.id = '1234'

        self.assertRaises(
            exceptions.ResourceTimeout,
            self.proxy.wait_for_nodes_provision_state,
            ['abcd', node.Node(id='1234')],
            'fake state',
            timeout=0.001,
        )
        mock_get.return_value._check_state_reached.assert_called_with(
            self.proxy, 'fake state', True
        )

    def test_timeout_no_fail(self, mock_get):
        mock_get.return_value._check_state_reached.return_value = False
        mock_get.return_value.id = '1234'

        result = self.proxy.wait_for_nodes_provision_state(
            ['abcd'], 'fake state', timeout=0.001, fail=False
        )
        mock_get.return_value._check_state_reached.assert_called_with(
            self.proxy, 'fake state', True
        )

        self.assertEqual([], result.success)
        self.assertEqual([mock_get.return_value], result.timeout)
        self.assertEqual([], result.failure)

    def test_timeout_and_failures_not_fail(self, mock_get):
        def _fake_get(_self, node):
            result = mock.Mock()
            result.id = getattr(node, 'id', node)
            if result.id == '1':
                result._check_state_reached.return_value = True
            elif result.id == '2':
                result._check_state_reached.side_effect = (
                    exceptions.ResourceFailure("boom")
                )
            else:
                result._check_state_reached.return_value = False
            return result

        mock_get.side_effect = _fake_get

        result = self.proxy.wait_for_nodes_provision_state(
            ['1', '2', '3'], 'fake state', timeout=0.001, fail=False
        )

        self.assertEqual(['1'], [x.id for x in result.success])
        self.assertEqual(['3'], [x.id for x in result.timeout])
        self.assertEqual(['2'], [x.id for x in result.failure])


class TestInspectionRules(TestBaremetalProxy):
    @mock.patch.object(inspection_rules.InspectionRule, 'list')
    def test_inspection_rules_detailed(self, mock_list):
        result = self.proxy.inspection_rules(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, details=True, query=1
        )

    @mock.patch.object(inspection_rules.InspectionRule, 'list')
    def test_inspection_rules_not_detailed(self, mock_list):
        result = self.proxy.inspection_rules(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy, paginated=True, base_path=None, query=1
        )

    def test_create_inspection_rule(self):
        self.verify_create(
            self.proxy.create_inspection_rule, inspection_rules.InspectionRule
        )

    def test_get_inspection_rule(self):
        self.verify_get(
            self.proxy.get_inspection_rule,
            inspection_rules.InspectionRule,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_update_inspection_rule(self):
        self.verify_update(
            self.proxy.update_inspection_rule, inspection_rules.InspectionRule
        )

    def test_delete_inspection_rule(self):
        self.verify_delete(
            self.proxy.delete_inspection_rule,
            inspection_rules.InspectionRule,
            False,
        )

    def test_delete_inspection_rule_ignore(self):
        self.verify_delete(
            self.proxy.delete_inspection_rule,
            inspection_rules.InspectionRule,
            True,
        )
