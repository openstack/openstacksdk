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

from keystoneauth1 import adapter
import mock

from openstack.baremetal.v1 import node
from openstack import exceptions
from openstack.tests.unit import base

# NOTE: Sample data from api-ref doc
FAKE = {
    "chassis_uuid": "1",  # NOTE: missed in api-ref sample
    "clean_step": {},
    "console_enabled": False,
    "created_at": "2016-08-18T22:28:48.643434+00:00",
    "driver": "agent_ipmitool",
    "driver_info": {
        "ipmi_password": "******",
        "ipmi_username": "ADMIN"
    },
    "driver_internal_info": {},
    "extra": {},
    "inspection_finished_at": None,
    "inspection_started_at": None,
    "instance_info": {},
    "instance_uuid": None,
    "last_error": None,
    "links": [
        {
            "href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/nodes/<NODE_ID>",
            "rel": "bookmark"
        }
    ],
    "maintenance": False,
    "maintenance_reason": None,
    "name": "test_node",
    "network_interface": "flat",
    "portgroups": [
        {
            "href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>/portgroups",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/nodes/<NODE_ID>/portgroups",
            "rel": "bookmark"
        }
    ],
    "ports": [
        {
            "href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>/ports",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/nodes/<NODE_ID>/ports",
            "rel": "bookmark"
        }
    ],
    "power_state": None,
    "properties": {},
    "provision_state": "enroll",
    "provision_updated_at": None,
    "raid_config": {},
    "reservation": None,
    "resource_class": None,
    "states": [
        {
            "href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>/states",
            "rel": "self"
        },
        {
            "href": "http://127.0.0.1:6385/nodes/<NODE_ID>/states",
            "rel": "bookmark"
        }
    ],
    "target_power_state": None,
    "target_provision_state": None,
    "target_raid_config": {},
    "updated_at": None,
    "uuid": "6d85703a-565d-469a-96ce-30b6de53079d"
}


class TestNode(base.TestCase):

    def test_basic(self):
        sot = node.Node()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('nodes', sot.resources_key)
        self.assertEqual('/nodes', sot.base_path)
        self.assertEqual('baremetal', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.update_method)

    def test_instantiate(self):
        sot = node.Node(**FAKE)

        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)

        self.assertEqual(FAKE['chassis_uuid'], sot.chassis_id)
        self.assertEqual(FAKE['clean_step'], sot.clean_step)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['driver'], sot.driver)
        self.assertEqual(FAKE['driver_info'], sot.driver_info)
        self.assertEqual(FAKE['driver_internal_info'],
                         sot.driver_internal_info)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['instance_info'], sot.instance_info)
        self.assertEqual(FAKE['instance_uuid'], sot.instance_id)
        self.assertEqual(FAKE['console_enabled'], sot.is_console_enabled)
        self.assertEqual(FAKE['maintenance'], sot.is_maintenance)
        self.assertEqual(FAKE['last_error'], sot.last_error)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['maintenance_reason'], sot.maintenance_reason)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['network_interface'], sot.network_interface)
        self.assertEqual(FAKE['ports'], sot.ports)
        self.assertEqual(FAKE['portgroups'], sot.port_groups)
        self.assertEqual(FAKE['power_state'], sot.power_state)
        self.assertEqual(FAKE['properties'], sot.properties)
        self.assertEqual(FAKE['provision_state'], sot.provision_state)
        self.assertEqual(FAKE['raid_config'], sot.raid_config)
        self.assertEqual(FAKE['reservation'], sot.reservation)
        self.assertEqual(FAKE['resource_class'], sot.resource_class)
        self.assertEqual(FAKE['states'], sot.states)
        self.assertEqual(FAKE['target_provision_state'],
                         sot.target_provision_state)
        self.assertEqual(FAKE['target_power_state'], sot.target_power_state)
        self.assertEqual(FAKE['target_raid_config'], sot.target_raid_config)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)


class TestNodeDetail(base.TestCase):

    def test_basic(self):
        sot = node.NodeDetail()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('nodes', sot.resources_key)
        self.assertEqual('/nodes/detail', sot.base_path)
        self.assertEqual('baremetal', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = node.NodeDetail(**FAKE)

        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)

        self.assertEqual(FAKE['chassis_uuid'], sot.chassis_id)
        self.assertEqual(FAKE['clean_step'], sot.clean_step)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['driver'], sot.driver)
        self.assertEqual(FAKE['driver_info'], sot.driver_info)
        self.assertEqual(FAKE['driver_internal_info'],
                         sot.driver_internal_info)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['instance_info'], sot.instance_info)
        self.assertEqual(FAKE['instance_uuid'], sot.instance_id)
        self.assertEqual(FAKE['console_enabled'], sot.is_console_enabled)
        self.assertEqual(FAKE['maintenance'], sot.is_maintenance)
        self.assertEqual(FAKE['last_error'], sot.last_error)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['maintenance_reason'], sot.maintenance_reason)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['network_interface'], sot.network_interface)
        self.assertEqual(FAKE['ports'], sot.ports)
        self.assertEqual(FAKE['portgroups'], sot.port_groups)
        self.assertEqual(FAKE['power_state'], sot.power_state)
        self.assertEqual(FAKE['properties'], sot.properties)
        self.assertEqual(FAKE['provision_state'], sot.provision_state)
        self.assertEqual(FAKE['raid_config'], sot.raid_config)
        self.assertEqual(FAKE['reservation'], sot.reservation)
        self.assertEqual(FAKE['resource_class'], sot.resource_class)
        self.assertEqual(FAKE['states'], sot.states)
        self.assertEqual(FAKE['target_provision_state'],
                         sot.target_provision_state)
        self.assertEqual(FAKE['target_power_state'], sot.target_power_state)
        self.assertEqual(FAKE['target_raid_config'], sot.target_raid_config)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)


@mock.patch('time.sleep', lambda _t: None)
@mock.patch.object(node.Node, 'get', autospec=True)
class TestNodeWaitForProvisionState(base.TestCase):
    def setUp(self):
        super(TestNodeWaitForProvisionState, self).setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock()

    def test_success(self, mock_get):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'manageable'
            self.assertIs(session, self.session)

        mock_get.side_effect = _get_side_effect

        node = self.node.wait_for_provision_state(self.session, 'manageable')
        self.assertIs(node, self.node)

    def test_failure(self, mock_get):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'deploy failed'
            self.assertIs(session, self.session)

        mock_get.side_effect = _get_side_effect

        self.assertRaisesRegex(exceptions.SDKException,
                               'failure state "deploy failed"',
                               self.node.wait_for_provision_state,
                               self.session, 'manageable')

    def test_enroll_as_failure(self, mock_get):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'enroll'
            self.node.last_error = 'power failure'
            self.assertIs(session, self.session)

        mock_get.side_effect = _get_side_effect

        self.assertRaisesRegex(exceptions.SDKException,
                               'failed to verify management credentials',
                               self.node.wait_for_provision_state,
                               self.session, 'manageable')

    def test_timeout(self, mock_get):
        self.assertRaises(exceptions.ResourceTimeout,
                          self.node.wait_for_provision_state,
                          self.session, 'manageable', timeout=0.001)

    def test_not_abort_on_failed_state(self, mock_get):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'deploy failed'
            self.assertIs(session, self.session)

        mock_get.side_effect = _get_side_effect

        self.assertRaises(exceptions.ResourceTimeout,
                          self.node.wait_for_provision_state,
                          self.session, 'manageable', timeout=0.001,
                          abort_on_failed_state=False)


@mock.patch.object(node.Node, 'get', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeSetProvisionState(base.TestCase):

    def setUp(self):
        super(TestNodeSetProvisionState, self).setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(spec=adapter.Adapter,
                                 default_microversion=None)

    def test_no_arguments(self):
        self.node.set_provision_state(self.session, 'manage')
