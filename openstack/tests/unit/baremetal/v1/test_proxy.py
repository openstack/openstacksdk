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

from openstack.baremetal.v1 import _proxy
from openstack.baremetal.v1 import allocation
from openstack.baremetal.v1 import chassis
from openstack.baremetal.v1 import driver
from openstack.baremetal.v1 import node
from openstack.baremetal.v1 import port
from openstack.baremetal.v1 import port_group
from openstack import exceptions
from openstack.tests.unit import base
from openstack.tests.unit import test_proxy_base


class TestBaremetalProxy(test_proxy_base.TestProxyBase):

    def setUp(self):
        super(TestBaremetalProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_drivers(self):
        self.verify_list(self.proxy.drivers, driver.Driver)

    def test_get_driver(self):
        self.verify_get(self.proxy.get_driver, driver.Driver)

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
        self.verify_find(self.proxy.find_chassis, chassis.Chassis)

    def test_get_chassis(self):
        self.verify_get(self.proxy.get_chassis, chassis.Chassis)

    def test_update_chassis(self):
        self.verify_update(self.proxy.update_chassis, chassis.Chassis)

    def test_delete_chassis(self):
        self.verify_delete(self.proxy.delete_chassis, chassis.Chassis, False)

    def test_delete_chassis_ignore(self):
        self.verify_delete(self.proxy.delete_chassis, chassis.Chassis, True)

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

    def test_create_node(self):
        self.verify_create(self.proxy.create_node, node.Node)

    def test_find_node(self):
        self.verify_find(self.proxy.find_node, node.Node)

    def test_get_node(self):
        self.verify_get(self.proxy.get_node, node.Node)

    @mock.patch.object(node.Node, 'commit', autospec=True)
    def test_update_node(self, mock_commit):
        self.proxy.update_node('uuid', instance_id='new value')
        mock_commit.assert_called_once_with(mock.ANY, self.proxy,
                                            retry_on_conflict=True)
        self.assertEqual('new value', mock_commit.call_args[0][0].instance_id)

    @mock.patch.object(node.Node, 'commit', autospec=True)
    def test_update_node_no_retries(self, mock_commit):
        self.proxy.update_node('uuid', instance_id='new value',
                               retry_on_conflict=False)
        mock_commit.assert_called_once_with(mock.ANY, self.proxy,
                                            retry_on_conflict=False)
        self.assertEqual('new value', mock_commit.call_args[0][0].instance_id)

    def test_delete_node(self):
        self.verify_delete(self.proxy.delete_node, node.Node, False)

    def test_delete_node_ignore(self):
        self.verify_delete(self.proxy.delete_node, node.Node, True)

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
        self.verify_find(self.proxy.find_port, port.Port)

    def test_get_port(self):
        self.verify_get(self.proxy.get_port, port.Port)

    def test_update_port(self):
        self.verify_update(self.proxy.update_port, port.Port)

    def test_delete_port(self):
        self.verify_delete(self.proxy.delete_port, port.Port, False)

    def test_delete_port_ignore(self):
        self.verify_delete(self.proxy.delete_port, port.Port, True)

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

    def test_create_allocation(self):
        self.verify_create(self.proxy.create_allocation, allocation.Allocation)

    def test_get_allocation(self):
        self.verify_get(self.proxy.get_allocation, allocation.Allocation)

    def test_delete_allocation(self):
        self.verify_delete(self.proxy.delete_allocation, allocation.Allocation,
                           False)

    def test_delete_allocation_ignore(self):
        self.verify_delete(self.proxy.delete_allocation, allocation.Allocation,
                           True)


@mock.patch('time.sleep', lambda _sec: None)
@mock.patch.object(_proxy.Proxy, 'get_node', autospec=True)
class TestWaitForNodesProvisionState(base.TestCase):

    def setUp(self):
        super(TestWaitForNodesProvisionState, self).setUp()
        self.session = mock.Mock()
        self.proxy = _proxy.Proxy(self.session)

    def test_success(self, mock_get):
        # two attempts, one node succeeds after the 1st
        nodes = [mock.Mock(spec=node.Node, id=str(i))
                 for i in range(3)]
        for i, n in enumerate(nodes):
            # 1st attempt on 1st node, 2nd attempt on 2nd node
            n._check_state_reached.return_value = not (i % 2)
        mock_get.side_effect = nodes

        result = self.proxy.wait_for_nodes_provision_state(
            ['abcd', node.Node(id='1234')], 'fake state')
        self.assertEqual([nodes[0], nodes[2]], result)

        for n in nodes:
            n._check_state_reached.assert_called_once_with(
                self.proxy, 'fake state', True)

    def test_timeout(self, mock_get):
        mock_get.return_value._check_state_reached.return_value = False
        mock_get.return_value.id = '1234'

        self.assertRaises(exceptions.ResourceTimeout,
                          self.proxy.wait_for_nodes_provision_state,
                          ['abcd', node.Node(id='1234')], 'fake state',
                          timeout=0.001)
        mock_get.return_value._check_state_reached.assert_called_with(
            self.proxy, 'fake state', True)
