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

    def test_operator_cloud(self):
        self.assertIsInstance(self.op_cloud, shade.OperatorCloud)

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
