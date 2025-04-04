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

from openstack.baremetal.v1 import _proxy
from openstack.baremetal.v1 import allocation
from openstack.baremetal.v1 import chassis
from openstack.baremetal.v1 import deploy_templates
from openstack.baremetal.v1 import driver
from openstack.baremetal.v1 import node
from openstack.baremetal.v1 import port
from openstack.baremetal.v1 import port_group
from openstack.baremetal.v1 import volume_connector
from openstack.baremetal.v1 import volume_target
from openstack import exceptions
from openstack.tests.unit import base
from openstack.tests.unit import test_proxy_base


_MOCK_METHOD = 'openstack.baremetal.v1._proxy.Proxy._get_with_fields'


class TestBaremetalProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestDrivers(TestBaremetalProxy):
    def test_drivers(self):
        self.verify_list(self.proxy.drivers, driver.Driver)

    def test_get_driver(self):
        self.verify_get(self.proxy.get_driver, driver.Driver)


class TestChassis(TestBaremetalProxy):
    @mock.patch.object(chassis.Chassis, 'list')
    def test_chassis_detailed(self, mock_list):
        result = self.proxy.chassis(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, details=True, query=1)

    @mock.patch.object(chassis.Chassis, 'list')
    def test_chassis_not_detailed(self, mock_list):
        result = self.proxy.chassis(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, details=False, query=1)

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
        mock_list.assert_called_once_with(self.proxy, details=True, query=1)

    @mock.patch.object(node.Node, 'list')
    def test_nodes_not_detailed(self, mock_list):
        result = self.proxy.nodes(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, details=False, query=1)

    @mock.patch.object(node.Node, 'list')
    def test_nodes_sharded(self, mock_list):
        kwargs = {"shard": 'meow', "query": 1}
        result = self.proxy.nodes(fields=("uuid", "instance_uuid"), **kwargs)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(
            self.proxy,
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


class TestPort(TestBaremetalProxy):
    @mock.patch.object(port.Port, 'list')
    def test_ports_detailed(self, mock_list):
        result = self.proxy.ports(details=True, query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, details=True, query=1)

    @mock.patch.object(port.Port, 'list')
    def test_ports_not_detailed(self, mock_list):
        result = self.proxy.ports(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, details=False, query=1)

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
        mock_list.assert_called_once_with(self.proxy, details=True, query=1)

    @mock.patch.object(port_group.PortGroup, 'list')
    def test_port_groups_not_detailed(self, mock_list):
        result = self.proxy.port_groups(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, details=False, query=1)

    def test_get_port_group(self):
        self.verify_get(
            self.proxy.get_port_group,
            port_group.PortGroup,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )


class TestAllocation(TestBaremetalProxy):
    def test_create_allocation(self):
        self.verify_create(self.proxy.create_allocation, allocation.Allocation)

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
        mock_list.assert_called_once_with(self.proxy, detail=True, query=1)

    @mock.patch.object(volume_target.VolumeTarget, 'list')
    def test_volume_target_not_detailed(self, mock_list):
        result = self.proxy.volume_targets(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, query=1)

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
        mock_list.assert_called_once_with(self.proxy, detail=True, query=1)

    @mock.patch.object(deploy_templates.DeployTemplate, 'list')
    def test_deploy_templates_not_detailed(self, mock_list):
        result = self.proxy.deploy_templates(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, query=1)

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
