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

from keystoneauth1 import plugin as ksa_plugin

from distutils import version as du_version
import mock
import munch
import testtools
import uuid

import os_client_config as occ
from os_client_config import cloud_config
import shade
from shade import exc
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


class TestShadeOperator(base.RequestsMockTestCase):

    def setUp(self):
        super(TestShadeOperator, self).setUp()
        self.machine_id = uuid.uuid4().hex
        self.machine_name = self.getUniqueString('machine')
        self.node = fakes.make_fake_machine(
            machine_id=self.machine_id,
            machine_name=self.machine_name)

    def get_ironic_mock_url(self, append=None, *args, **kwargs):
        if append:
            # TODO(mordred): Remove when we do version discovery
            # properly everywhere
            append.insert(0, 'v1')
        return self.get_mock_url('baremetal', append=append, *args, **kwargs)

    def test_operator_cloud(self):
        self.assertIsInstance(self.op_cloud, shade.OperatorCloud)

    def test_get_machine(self):

        self.register_uris([
            dict(method='GET',
                 uri=self.get_ironic_mock_url(
                     append=['nodes', self.machine_name]),
                 json=self.node),
        ])
        machine = self.op_cloud.get_machine(self.machine_name)
        self.assertEqual(self.node, machine)

        self.assert_calls()

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_get_machine_by_mac(self, mock_client):
        class port_value(object):
            node_uuid = '00000000-0000-0000-0000-000000000000'
            address = '00:00:00:00:00:00'

        class node_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'

        expected_value = dict(
            uuid='00000000-0000-0000-0000-000000000000')

        mock_client.port.get_by_address.return_value = port_value
        mock_client.node.get.return_value = node_value
        machine = self.op_cloud.get_machine_by_mac('00:00:00:00:00:00')
        mock_client.port.get_by_address.assert_called_with(
            address='00:00:00:00:00:00')
        mock_client.node.get.assert_called_with(
            node_id='00000000-0000-0000-0000-000000000000')
        self.assertEqual(machine, expected_value)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_list_machines(self, mock_client):
        m1 = fakes.FakeMachine(1, 'fake_machine1')
        mock_client.node.list.return_value = [m1]
        machines = self.op_cloud.list_machines()
        self.assertTrue(mock_client.node.list.called)
        self.assertEqual(meta.obj_to_munch(m1), machines[0])

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_validate_node(self, mock_client):
        node_uuid = '123'
        self.op_cloud.validate_node(node_uuid)
        mock_client.node.validate.assert_called_once_with(
            node_uuid=node_uuid
        )

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_list_nics(self, mock_client):
        port1 = fakes.FakeMachinePort(1, "aa:bb:cc:dd", "node1")
        port2 = fakes.FakeMachinePort(2, "dd:cc:bb:aa", "node2")
        port_list = [port1, port2]
        port_dict_list = meta.obj_list_to_munch(port_list)

        mock_client.port.list.return_value = port_list
        nics = self.op_cloud.list_nics()

        self.assertTrue(mock_client.port.list.called)
        self.assertEqual(port_dict_list, nics)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_list_nics_failure(self, mock_client):
        mock_client.port.list.side_effect = Exception()
        self.assertRaises(exc.OpenStackCloudException,
                          self.op_cloud.list_nics)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_list_nics_for_machine(self, mock_client):
        mock_client.node.list_ports.return_value = []
        self.op_cloud.list_nics_for_machine("123")
        mock_client.node.list_ports.assert_called_with(node_id="123")

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_list_nics_for_machine_failure(self, mock_client):
        mock_client.node.list_ports.side_effect = Exception()
        self.assertRaises(exc.OpenStackCloudException,
                          self.op_cloud.list_nics_for_machine, None)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_patch_machine(self, mock_client):
        node_id = 'node01'
        patch = []
        patch.append({'op': 'remove', 'path': '/instance_info'})
        self.op_cloud.patch_machine(node_id, patch)
        self.assertTrue(mock_client.node.update.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_no_action(self, mock_patch, mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'node01'

        expected_machine = dict(
            uuid='00000000-0000-0000-0000-000000000000',
            name='node01'
        )
        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine('node01')
        self.assertIsNone(update_dict['changes'])
        self.assertFalse(mock_patch.called)
        self.assertDictEqual(expected_machine, update_dict['node'])

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_no_action_name(self, mock_patch,
                                                 mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'node01'

        expected_machine = dict(
            uuid='00000000-0000-0000-0000-000000000000',
            name='node01'
        )
        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine('node01', name='node01')
        self.assertIsNone(update_dict['changes'])
        self.assertFalse(mock_patch.called)
        self.assertDictEqual(expected_machine, update_dict['node'])

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_action_name(self, mock_patch,
                                              mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'evil'

        expected_patch = [dict(op='replace', path='/name', value='good')]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine('evil', name='good')
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/name', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_name(self, mock_patch,
                                              mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            name = 'evil'

        expected_patch = [dict(op='replace', path='/name', value='good')]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine('evil', name='good')
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/name', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_chassis_uuid(self, mock_patch,
                                                      mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            chassis_uuid = None

        expected_patch = [
            dict(
                op='replace',
                path='/chassis_uuid',
                value='00000000-0000-0000-0000-000000000001'
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            chassis_uuid='00000000-0000-0000-0000-000000000001')
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/chassis_uuid', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_driver(self, mock_patch,
                                                mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            driver = None

        expected_patch = [
            dict(
                op='replace',
                path='/driver',
                value='fake'
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            driver='fake'
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/driver', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_driver_info(self, mock_patch,
                                                     mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            driver_info = None

        expected_patch = [
            dict(
                op='replace',
                path='/driver_info',
                value=dict(var='fake')
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            driver_info=dict(var="fake")
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/driver_info', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_instance_info(self, mock_patch,
                                                       mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            instance_info = None

        expected_patch = [
            dict(
                op='replace',
                path='/instance_info',
                value=dict(var='fake')
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            instance_info=dict(var="fake")
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/instance_info', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_instance_uuid(self, mock_patch,
                                                       mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            instance_uuid = None

        expected_patch = [
            dict(
                op='replace',
                path='/instance_uuid',
                value='00000000-0000-0000-0000-000000000002'
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            instance_uuid='00000000-0000-0000-0000-000000000002'
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/instance_uuid', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'patch_machine')
    def test_update_machine_patch_update_properties(self, mock_patch,
                                                    mock_client):
        class client_return_value(object):
            uuid = '00000000-0000-0000-0000-000000000000'
            properties = None

        expected_patch = [
            dict(
                op='replace',
                path='/properties',
                value=dict(var='fake')
            )]

        mock_client.node.get.return_value = client_return_value

        update_dict = self.op_cloud.update_machine(
            '00000000-0000-0000-0000-000000000000',
            properties=dict(var="fake")
        )
        self.assertIsNotNone(update_dict['changes'])
        self.assertEqual('/properties', update_dict['changes'][0])
        self.assertTrue(mock_patch.called)
        mock_patch.assert_called_with(
            '00000000-0000-0000-0000-000000000000',
            expected_patch)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_inspect_machine_fail_active(self, mock_client):

        machine_uuid = '00000000-0000-0000-0000-000000000000'

        class active_machine(object):
            uuid = machine_uuid
            provision_state = "active"

        mock_client.node.get.return_value = active_machine
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.inspect_machine,
            machine_uuid,
            wait=True,
            timeout=1)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_inspect_machine_failed(self, mock_client):

        machine_uuid = '00000000-0000-0000-0000-000000000000'

        class inspect_failed_machine(object):
            uuid = machine_uuid
            provision_state = "inspect failed"
            last_error = "kaboom"

        mock_client.node.get.return_value = inspect_failed_machine
        self.op_cloud.inspect_machine(machine_uuid)
        self.assertTrue(mock_client.node.set_provision_state.called)
        self.assertEqual(
            mock_client.node.set_provision_state.call_count, 1)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_inspect_machine_managable(self, mock_client):

        machine_uuid = '00000000-0000-0000-0000-000000000000'

        class manageable_machine(object):
            uuid = machine_uuid
            provision_state = "manageable"

        mock_client.node.get.return_value = manageable_machine
        self.op_cloud.inspect_machine(machine_uuid)
        self.assertEqual(
            mock_client.node.set_provision_state.call_count, 1)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_inspect_machine_available(self, mock_client):

        machine_uuid = '00000000-0000-0000-0000-000000000000'

        class available_machine(object):
            uuid = machine_uuid
            provision_state = "available"

        class manageable_machine(object):
            uuid = machine_uuid
            provision_state = "manageable"

        class inspecting_machine(object):
            uuid = machine_uuid
            provision_state = "inspecting"

        mock_client.node.get.side_effect = iter([
            available_machine,
            available_machine,
            manageable_machine,
            manageable_machine,
            inspecting_machine])
        self.op_cloud.inspect_machine(machine_uuid)
        self.assertTrue(mock_client.node.set_provision_state.called)
        self.assertEqual(
            mock_client.node.set_provision_state.call_count, 3)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_inspect_machine_available_wait(self, mock_client):

        machine_uuid = '00000000-0000-0000-0000-000000000000'

        class available_machine(object):
            uuid = machine_uuid
            provision_state = "available"

        class manageable_machine(object):
            uuid = machine_uuid
            provision_state = "manageable"

        class inspecting_machine(object):
            uuid = machine_uuid
            provision_state = "inspecting"

        mock_client.node.get.side_effect = iter([
            available_machine,
            available_machine,
            manageable_machine,
            inspecting_machine,
            manageable_machine,
            available_machine,
            available_machine])
        expected_return_value = dict(
            uuid=machine_uuid,
            provision_state="available"
        )

        return_value = self.op_cloud.inspect_machine(
            machine_uuid, wait=True, timeout=1)
        self.assertTrue(mock_client.node.set_provision_state.called)
        self.assertEqual(
            mock_client.node.set_provision_state.call_count, 3)
        self.assertDictEqual(expected_return_value, return_value)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_inspect_machine_wait(self, mock_client):

        machine_uuid = '00000000-0000-0000-0000-000000000000'

        class manageable_machine(object):
            uuid = machine_uuid
            provision_state = "manageable"

        class inspecting_machine(object):
            uuid = machine_uuid
            provision_state = "inspecting"

        expected_return_value = dict(
            uuid=machine_uuid,
            provision_state="manageable"
        )
        mock_client.node.get.side_effect = iter([
            manageable_machine,
            inspecting_machine,
            inspecting_machine,
            manageable_machine,
            manageable_machine])

        return_value = self.op_cloud.inspect_machine(
            machine_uuid, wait=True, timeout=1)
        self.assertDictEqual(expected_return_value, return_value)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_inspect_machine_inspect_failed(self, mock_client):

        machine_uuid = '00000000-0000-0000-0000-000000000000'

        class manageable_machine(object):
            uuid = machine_uuid
            provision_state = "manageable"
            last_error = None

        class inspecting_machine(object):
            uuid = machine_uuid
            provision_state = "inspecting"
            last_error = None

        class inspect_failed_machine(object):
            uuid = machine_uuid
            provision_state = "inspect failed"
            last_error = "kaboom"

        mock_client.node.get.side_effect = iter([
            manageable_machine,
            inspecting_machine,
            inspect_failed_machine])
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.inspect_machine,
            machine_uuid,
            wait=True,
            timeout=1)
        self.assertEqual(
            mock_client.node.set_provision_state.call_count, 1)
        self.assertEqual(mock_client.node.get.call_count, 3)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_register_machine(self, mock_client):
        class fake_node(object):
            uuid = "00000000-0000-0000-0000-000000000000"
            provision_state = "available"
            reservation = None
            last_error = None

        expected_return_value = dict(
            uuid="00000000-0000-0000-0000-000000000000",
            provision_state="available",
            reservation=None,
            last_error=None
        )
        mock_client.node.create.return_value = fake_node
        mock_client.node.get.return_value = fake_node
        nics = [{'mac': '00:00:00:00:00:00'}]
        return_value = self.op_cloud.register_machine(nics)
        self.assertDictEqual(expected_return_value, return_value)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)
        self.assertFalse(mock_client.node.get.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'node_set_provision_state')
    def test_register_machine_enroll(
            self,
            mock_set_state,
            mock_client):
        machine_uuid = "00000000-0000-0000-0000-000000000000"

        class fake_node_init_state(object):
            uuid = machine_uuid
            provision_state = "enroll"
            reservation = None
            last_error = None

        class fake_node_post_manage(object):
            uuid = machine_uuid
            provision_state = "enroll"
            reservation = "do you have a flag?"
            last_error = None

        class fake_node_post_manage_done(object):
            uuid = machine_uuid
            provision_state = "manage"
            reservation = None
            last_error = None

        class fake_node_post_provide(object):
            uuid = machine_uuid
            provision_state = "available"
            reservation = None
            last_error = None

        class fake_node_post_enroll_failure(object):
            uuid = machine_uuid
            provision_state = "enroll"
            reservation = None
            last_error = "insufficent lolcats"

        expected_return_value = dict(
            uuid=machine_uuid,
            provision_state="available",
            reservation=None,
            last_error=None
        )

        mock_client.node.get.side_effect = iter([
            fake_node_init_state,
            fake_node_post_manage,
            fake_node_post_manage_done,
            fake_node_post_provide])
        mock_client.node.create.return_value = fake_node_init_state
        nics = [{'mac': '00:00:00:00:00:00'}]
        return_value = self.op_cloud.register_machine(nics)
        self.assertDictEqual(expected_return_value, return_value)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)
        self.assertTrue(mock_client.node.get.called)
        mock_client.reset_mock()
        mock_client.node.get.side_effect = iter([
            fake_node_init_state,
            fake_node_post_manage,
            fake_node_post_manage_done,
            fake_node_post_provide])
        return_value = self.op_cloud.register_machine(nics, wait=True)
        self.assertDictEqual(expected_return_value, return_value)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)
        self.assertTrue(mock_client.node.get.called)
        mock_client.reset_mock()
        mock_client.node.get.side_effect = iter([
            fake_node_init_state,
            fake_node_post_manage,
            fake_node_post_enroll_failure])
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.register_machine,
            nics)
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.register_machine,
            nics,
            wait=True)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade.OperatorCloud, 'node_set_provision_state')
    def test_register_machine_enroll_timeout(
            self,
            mock_set_state,
            mock_client):
        machine_uuid = "00000000-0000-0000-0000-000000000000"

        class fake_node_init_state(object):
            uuid = machine_uuid
            provision_state = "enroll"
            reservation = "do you have a flag?"
            last_error = None

        mock_client.node.get.return_value = fake_node_init_state
        mock_client.node.create.return_value = fake_node_init_state
        nics = [{'mac': '00:00:00:00:00:00'}]
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.register_machine,
            nics,
            lock_timeout=0.001)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)
        self.assertTrue(mock_client.node.get.called)
        mock_client.node.get.reset_mock()
        mock_client.node.create.reset_mock()
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.register_machine,
            nics,
            wait=True,
            timeout=0.001)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)
        self.assertTrue(mock_client.node.get.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_register_machine_port_create_failed(self, mock_client):
        class fake_node(object):
            uuid = "00000000-0000-0000-0000-000000000000"
            provision_state = "available"
            resevation = None
            last_error = None

        nics = [{'mac': '00:00:00:00:00:00'}]
        mock_client.node.create.return_value = fake_node
        mock_client.port.create.side_effect = (
            exc.OpenStackCloudException("Error"))
        self.assertRaises(exc.OpenStackCloudException,
                          self.op_cloud.register_machine,
                          nics)
        self.assertTrue(mock_client.node.create.called)
        self.assertTrue(mock_client.port.create.called)
        self.assertTrue(mock_client.node.delete.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_unregister_machine(self, mock_client):
        class fake_node(object):
            provision_state = 'available'

        class fake_port(object):
            uuid = '00000000-0000-0000-0000-000000000001'

        mock_client.port.get_by_address.return_value = fake_port
        mock_client.node.get.return_value = fake_node
        nics = [{'mac': '00:00:00:00:00:00'}]
        uuid = "00000000-0000-0000-0000-000000000000"
        self.op_cloud.unregister_machine(nics, uuid)
        self.assertTrue(mock_client.node.delete.called)
        self.assertTrue(mock_client.port.get_by_address.called)
        self.assertTrue(mock_client.port.delete.called)
        self.assertTrue(mock_client.port.get_by_address.called)
        mock_client.port.get_by_address.assert_called_with(
            address='00:00:00:00:00:00')
        mock_client.port.delete.assert_called_with(
            port_id='00000000-0000-0000-0000-000000000001')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_unregister_machine_unavailable(self, mock_client):
        invalid_states = ['active', 'cleaning', 'clean wait', 'clean failed']
        nics = [{'mac': '00:00:00:00:00:00'}]
        uuid = "00000000-0000-0000-0000-000000000000"
        for state in invalid_states:
            class fake_node(object):
                provision_state = state

            mock_client.node.get.return_value = fake_node
            self.assertRaises(
                exc.OpenStackCloudException,
                self.op_cloud.unregister_machine,
                nics,
                uuid)
            self.assertFalse(mock_client.node.delete.called)
            self.assertFalse(mock_client.port.delete.called)
            self.assertFalse(mock_client.port.get_by_address.called)
            self.assertTrue(mock_client.node.get.called)
            mock_client.node.reset_mock()
            mock_client.node.reset_mock()

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_unregister_machine_timeout(self, mock_client):
        class fake_node(object):
            provision_state = 'available'

        mock_client.node.get.return_value = fake_node
        nics = [{'mac': '00:00:00:00:00:00'}]
        uuid = "00000000-0000-0000-0000-000000000000"
        self.assertRaises(
            exc.OpenStackCloudException,
            self.op_cloud.unregister_machine,
            nics,
            uuid,
            wait=True,
            timeout=0.001)
        self.assertTrue(mock_client.node.delete.called)
        self.assertTrue(mock_client.port.delete.called)
        self.assertTrue(mock_client.port.get_by_address.called)
        self.assertTrue(mock_client.node.get.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_set_machine_maintenace_state(self, mock_client):
        mock_client.node.set_maintenance.return_value = None
        node_id = 'node01'
        reason = 'no reason'
        self.op_cloud.set_machine_maintenance_state(
            node_id, True, reason=reason)
        mock_client.node.set_maintenance.assert_called_with(
            node_id='node01',
            state='true',
            maint_reason='no reason')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_set_machine_maintenace_state_false(self, mock_client):
        mock_client.node.set_maintenance.return_value = None
        node_id = 'node01'
        self.op_cloud.set_machine_maintenance_state(node_id, False)
        mock_client.node.set_maintenance.assert_called_with(
            node_id='node01',
            state='false')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_remove_machine_from_maintenance(self, mock_client):
        mock_client.node.set_maintenance.return_value = None
        node_id = 'node01'
        self.op_cloud.remove_machine_from_maintenance(node_id)
        mock_client.node.set_maintenance.assert_called_with(
            node_id='node01',
            state='false')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_set_machine_power_on(self, mock_client):
        mock_client.node.set_power_state.return_value = None
        node_id = 'node01'
        return_value = self.op_cloud.set_machine_power_on(node_id)
        self.assertEqual(None, return_value)
        mock_client.node.set_power_state.assert_called_with(
            node_id='node01',
            state='on')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_set_machine_power_off(self, mock_client):
        mock_client.node.set_power_state.return_value = None
        node_id = 'node01'
        return_value = self.op_cloud.set_machine_power_off(node_id)
        self.assertEqual(None, return_value)
        mock_client.node.set_power_state.assert_called_with(
            node_id='node01',
            state='off')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_set_machine_power_reboot(self, mock_client):
        mock_client.node.set_power_state.return_value = None
        node_id = 'node01'
        return_value = self.op_cloud.set_machine_power_reboot(node_id)
        self.assertEqual(None, return_value)
        mock_client.node.set_power_state.assert_called_with(
            node_id='node01',
            state='reboot')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_set_machine_power_reboot_failure(self, mock_client):
        mock_client.node.set_power_state.return_value = 'failure'
        self.assertRaises(shade.OpenStackCloudException,
                          self.op_cloud.set_machine_power_reboot,
                          'node01')
        mock_client.node.set_power_state.assert_called_with(
            node_id='node01',
            state='reboot')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_node_set_provision_state(self, mock_client):

        class active_node_state(object):
            provision_state = "active"

        active_return_value = dict(
            provision_state="active")

        mock_client.node.set_provision_state.return_value = None
        mock_client.node.get.return_value = active_node_state
        node_id = 'node01'
        return_value = self.op_cloud.node_set_provision_state(
            node_id,
            'active',
            configdrive='http://127.0.0.1/file.iso')
        self.assertEqual(active_return_value, return_value)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node01',
            state='active',
            configdrive='http://127.0.0.1/file.iso')
        self.assertTrue(mock_client.node.get.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_node_set_provision_state_wait_timeout(self, mock_client):
        class deploying_node_state(object):
            provision_state = "deploying"

        class active_node_state(object):
            provision_state = "active"

        class managable_node_state(object):
            provision_state = "managable"

        class available_node_state(object):
            provision_state = "available"

        active_return_value = dict(
            provision_state="active")
        mock_client.node.get.return_value = active_node_state
        mock_client.node.set_provision_state.return_value = None
        node_id = 'node01'
        return_value = self.op_cloud.node_set_provision_state(
            node_id,
            'active',
            configdrive='http://127.0.0.1/file.iso',
            wait=True)

        self.assertEqual(active_return_value, return_value)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node01',
            state='active',
            configdrive='http://127.0.0.1/file.iso')
        self.assertTrue(mock_client.node.get.called)
        mock_client.mock_reset()
        mock_client.node.get.return_value = deploying_node_state
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.node_set_provision_state,
            node_id,
            'active',
            configdrive='http://127.0.0.1/file.iso',
            wait=True,
            timeout=0.001)
        self.assertTrue(mock_client.node.get.called)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node01',
            state='active',
            configdrive='http://127.0.0.1/file.iso')

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_node_set_provision_state_wait_failure(self, mock_client):
        class active_node_state(object):
            provision_state = "active"

        class deploy_failed_node_state(object):
            provision_state = "deploy failed"

        class clean_failed_node_state(object):
            provision_state = "clean failed"

        active_return_value = dict(
            provision_state="active")
        mock_client.node.get.return_value = active_node_state
        mock_client.node.set_provision_state.return_value = None
        node_id = 'node01'
        return_value = self.op_cloud.node_set_provision_state(
            node_id,
            'active',
            configdrive='http://127.0.0.1/file.iso',
            wait=True)

        self.assertEqual(active_return_value, return_value)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node01',
            state='active',
            configdrive='http://127.0.0.1/file.iso')
        self.assertTrue(mock_client.node.get.called)
        mock_client.mock_reset()
        mock_client.node.get.return_value = deploy_failed_node_state
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.node_set_provision_state,
            node_id,
            'active',
            configdrive='http://127.0.0.1/file.iso',
            wait=True,
            timeout=300)
        self.assertTrue(mock_client.node.get.called)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node01',
            state='active',
            configdrive='http://127.0.0.1/file.iso')
        mock_client.mock_reset()
        mock_client.node.get.return_value = clean_failed_node_state
        self.assertRaises(
            shade.OpenStackCloudException,
            self.op_cloud.node_set_provision_state,
            node_id,
            'deleted',
            wait=True,
            timeout=300)
        self.assertTrue(mock_client.node.get.called)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node01',
            state='deleted',
            configdrive=None)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_node_set_provision_state_wait_provide(self, mock_client):

        class managable_node_state(object):
            provision_state = "managable"

        class available_node_state(object):
            provision_state = "available"

        node_provide_return_value = dict(
            provision_state="available")

        mock_client.node.get.side_effect = iter([
            managable_node_state,
            available_node_state])
        return_value = self.op_cloud.node_set_provision_state(
            'test_node',
            'provide',
            wait=True)
        self.assertEqual(mock_client.node.get.call_count, 2)
        self.assertDictEqual(node_provide_return_value, return_value)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade._utils, '_iterate_timeout')
    def test_activate_node(self, mock_timeout, mock_client):
        mock_client.node.set_provision_state.return_value = None
        node_id = 'node02'
        return_value = self.op_cloud.activate_node(
            node_id,
            configdrive='http://127.0.0.1/file.iso')
        self.assertEqual(None, return_value)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node02',
            state='active',
            configdrive='http://127.0.0.1/file.iso')
        self.assertFalse(mock_timeout.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_activate_node_timeout(self, mock_client):

        class active_node_state(object):
            provision_state = 'active'

        class available_node_state(object):
            provision_state = 'available'

        mock_client.node.get.side_effect = iter([
            available_node_state,
            active_node_state])

        mock_client.node.set_provision_state.return_value = None
        node_id = 'node04'
        return_value = self.op_cloud.activate_node(
            node_id,
            configdrive='http://127.0.0.1/file.iso',
            wait=True,
            timeout=2)
        self.assertEqual(None, return_value)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node04',
            state='active',
            configdrive='http://127.0.0.1/file.iso')
        self.assertEqual(mock_client.node.get.call_count, 2)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    @mock.patch.object(shade._utils, '_iterate_timeout')
    def test_deactivate_node(self, mock_timeout, mock_client):
        mock_client.node.set_provision_state.return_value = None
        node_id = 'node03'
        return_value = self.op_cloud.deactivate_node(
            node_id, wait=False)
        self.assertEqual(None, return_value)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node03',
            state='deleted',
            configdrive=None)
        self.assertFalse(mock_timeout.called)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_deactivate_node_timeout(self, mock_client):

        class active_node_state(object):
            provision_state = 'active'

        class deactivated_node_state(object):
            provision_state = 'available'

        mock_client.node.get.side_effect = iter([
            active_node_state,
            deactivated_node_state])

        mock_client.node.set_provision_state.return_value = None
        node_id = 'node03'
        return_value = self.op_cloud.deactivate_node(
            node_id, wait=True, timeout=2)
        self.assertEqual(None, return_value)
        mock_client.node.set_provision_state.assert_called_with(
            node_uuid='node03',
            state='deleted',
            configdrive=None)
        self.assertEqual(mock_client.node.get.call_count, 2)

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_set_node_instance_info(self, mock_client):
        uuid = 'aaa'
        patch = [{'op': 'add', 'foo': 'bar'}]
        self.op_cloud.set_node_instance_info(uuid, patch)
        mock_client.node.update.assert_called_with(
            node_id=uuid, patch=patch
        )

    @mock.patch.object(shade.OperatorCloud, 'ironic_client')
    def test_purge_node_instance_info(self, mock_client):
        uuid = 'aaa'
        expected_patch = [{'op': 'remove', 'path': '/instance_info'}]
        self.op_cloud.purge_node_instance_info(uuid)
        mock_client.node.update.assert_called_with(
            node_id=uuid, patch=expected_patch
        )

    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_get_image_name(self, mock_client):

        fake_image = munch.Munch(
            id='22',
            name='22 name',
            status='success')
        mock_client.get.return_value = [fake_image]
        self.assertEqual('22 name', self.op_cloud.get_image_name('22'))
        self.assertEqual('22 name', self.op_cloud.get_image_name('22 name'))

    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_get_image_id(self, mock_client):

        fake_image = munch.Munch(
            id='22',
            name='22 name',
            status='success')
        mock_client.get.return_value = [fake_image]
        self.assertEqual('22', self.op_cloud.get_image_id('22'))
        self.assertEqual('22', self.op_cloud.get_image_id('22 name'))

    @mock.patch.object(cloud_config.CloudConfig, 'get_endpoint')
    def test_get_session_endpoint_provided(self, fake_get_endpoint):
        fake_get_endpoint.return_value = 'http://fake.url'
        self.assertEqual(
            'http://fake.url', self.op_cloud.get_session_endpoint('image'))

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    def test_get_session_endpoint_session(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = 'http://fake.url'
        get_session_mock.return_value = session_mock
        self.assertEqual(
            'http://fake.url', self.op_cloud.get_session_endpoint('image'))

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    def test_get_session_endpoint_exception(self, get_session_mock):
        class FakeException(Exception):
            pass

        def side_effect(*args, **kwargs):
            raise FakeException("No service")
        session_mock = mock.Mock()
        session_mock.get_endpoint.side_effect = side_effect
        get_session_mock.return_value = session_mock
        self.op_cloud.name = 'testcloud'
        self.op_cloud.region_name = 'testregion'
        with testtools.ExpectedException(
                exc.OpenStackCloudException,
                "Error getting image endpoint on testcloud:testregion:"
                " No service"):
            self.op_cloud.get_session_endpoint("image")

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    def test_get_session_endpoint_unavailable(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = None
        get_session_mock.return_value = session_mock
        image_endpoint = self.op_cloud.get_session_endpoint("image")
        self.assertIsNone(image_endpoint)

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    def test_get_session_endpoint_identity(self, get_session_mock):
        session_mock = mock.Mock()
        get_session_mock.return_value = session_mock
        self.op_cloud.get_session_endpoint('identity')
        # occ > 1.26.0 fixes keystoneclient construction. Unfortunately, it
        # breaks our mocking of what keystoneclient does here. Since we're
        # close to just getting rid of ksc anyway, just put in a version match
        occ_version = du_version.StrictVersion(occ.__version__)
        if occ_version > du_version.StrictVersion('1.26.0'):
            kwargs = dict(
                interface='public', region_name='RegionOne',
                service_name=None, service_type='identity')
        else:
            kwargs = dict(interface=ksa_plugin.AUTH_INTERFACE)

        session_mock.get_endpoint.assert_called_with(**kwargs)

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    def test_has_service_no(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = None
        get_session_mock.return_value = session_mock
        self.assertFalse(self.op_cloud.has_service("image"))

    @mock.patch.object(cloud_config.CloudConfig, 'get_session')
    def test_has_service_yes(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = 'http://fake.url'
        get_session_mock.return_value = session_mock
        self.assertTrue(self.op_cloud.has_service("image"))

    def test_list_hypervisors(self):
        '''This test verifies that calling list_hypervisors results in a call
        to nova client.'''
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-hypervisors', 'detail']),
                 json={'hypervisors': [
                     fakes.make_fake_hypervisor('1', 'testserver1'),
                     fakes.make_fake_hypervisor('2', 'testserver2'),
                 ]}),
        ])

        r = self.op_cloud.list_hypervisors()

        self.assertEqual(2, len(r))
        self.assertEqual('testserver1', r[0]['hypervisor_hostname'])
        self.assertEqual('testserver2', r[1]['hypervisor_hostname'])

        self.assert_calls()
