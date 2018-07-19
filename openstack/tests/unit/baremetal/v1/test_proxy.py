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

import deprecation
import mock

from openstack.baremetal.v1 import _proxy
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
        self.verify_list(self.proxy.drivers, driver.Driver, paginated=False)

    def test_get_driver(self):
        self.verify_get(self.proxy.get_driver, driver.Driver)

    def test_chassis_detailed(self):
        self.verify_list(self.proxy.chassis, chassis.ChassisDetail,
                         paginated=True,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_chassis_not_detailed(self):
        self.verify_list(self.proxy.chassis, chassis.Chassis,
                         paginated=True,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

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

    def test_nodes_detailed(self):
        self.verify_list(self.proxy.nodes, node.NodeDetail,
                         paginated=True,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_nodes_not_detailed(self):
        self.verify_list(self.proxy.nodes, node.Node,
                         paginated=True,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    def test_create_node(self):
        self.verify_create(self.proxy.create_node, node.Node)

    def test_find_node(self):
        self.verify_find(self.proxy.find_node, node.Node)

    def test_get_node(self):
        self.verify_get(self.proxy.get_node, node.Node)

    def test_update_node(self):
        self.verify_update(self.proxy.update_node, node.Node)

    def test_delete_node(self):
        self.verify_delete(self.proxy.delete_node, node.Node, False)

    def test_delete_node_ignore(self):
        self.verify_delete(self.proxy.delete_node, node.Node, True)

    def test_ports_detailed(self):
        self.verify_list(self.proxy.ports, port.PortDetail,
                         paginated=True,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    def test_ports_not_detailed(self):
        self.verify_list(self.proxy.ports, port.Port,
                         paginated=True,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

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

    @deprecation.fail_if_not_removed
    def test_portgroups_detailed(self):
        self.verify_list(self.proxy.portgroups, port_group.PortGroupDetail,
                         paginated=True,
                         method_kwargs={"details": True, "query": 1},
                         expected_kwargs={"query": 1})

    @deprecation.fail_if_not_removed
    def test_portgroups_not_detailed(self):
        self.verify_list(self.proxy.portgroups, port_group.PortGroup,
                         paginated=True,
                         method_kwargs={"details": False, "query": 1},
                         expected_kwargs={"query": 1})

    @deprecation.fail_if_not_removed
    def test_create_portgroup(self):
        self.verify_create(self.proxy.create_portgroup, port_group.PortGroup)

    @deprecation.fail_if_not_removed
    def test_find_portgroup(self):
        self.verify_find(self.proxy.find_portgroup, port_group.PortGroup)

    @deprecation.fail_if_not_removed
    def test_get_portgroup(self):
        self.verify_get(self.proxy.get_portgroup, port_group.PortGroup)

    @deprecation.fail_if_not_removed
    def test_update_portgroup(self):
        self.verify_update(self.proxy.update_portgroup, port_group.PortGroup)

    @deprecation.fail_if_not_removed
    def test_delete_portgroup(self):
        self.verify_delete(self.proxy.delete_portgroup, port_group.PortGroup,
                           False)

    @deprecation.fail_if_not_removed
    def test_delete_portgroup_ignore(self):
        self.verify_delete(self.proxy.delete_portgroup, port_group.PortGroup,
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
