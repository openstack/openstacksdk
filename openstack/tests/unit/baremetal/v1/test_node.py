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

import base64
from unittest import mock

from keystoneauth1 import adapter

from openstack.baremetal.v1 import _common
from openstack.baremetal.v1 import node
from openstack import exceptions
from openstack import resource
from openstack.tests.unit import base
from openstack import utils

# NOTE: Sample data from api-ref doc
FAKE = {
    "automated_clean": False,
    "boot_mode": "uefi",
    "chassis_uuid": "1",  # NOTE: missed in api-ref sample
    "clean_step": {},
    "conductor_group": None,
    "console_enabled": False,
    "created_at": "2016-08-18T22:28:48.643434+00:00",
    "description": "A node.",
    "driver": "agent_ipmitool",
    "driver_info": {"ipmi_password": "******", "ipmi_username": "ADMIN"},
    "driver_internal_info": {},
    "extra": {},
    "firmware_interface": None,
    "inspection_finished_at": None,
    "inspection_started_at": None,
    "instance_info": {},
    "instance_uuid": None,
    "last_error": None,
    "lessee": None,
    "links": [
        {"href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>", "rel": "self"},
        {"href": "http://127.0.0.1:6385/nodes/<NODE_ID>", "rel": "bookmark"},
    ],
    "maintenance": False,
    "maintenance_reason": None,
    "name": "test_node",
    "network_interface": "flat",
    "owner": "4b7ed919-e4a6-4017-a081-43205c5b0b73",
    "parent_node": None,
    "portgroups": [
        {
            "href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>/portgroups",
            "rel": "self",
        },
        {
            "href": "http://127.0.0.1:6385/nodes/<NODE_ID>/portgroups",
            "rel": "bookmark",
        },
    ],
    "ports": [
        {
            "href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>/ports",
            "rel": "self",
        },
        {
            "href": "http://127.0.0.1:6385/nodes/<NODE_ID>/ports",
            "rel": "bookmark",
        },
    ],
    "power_state": None,
    "properties": {},
    "provision_state": "enroll",
    "provision_updated_at": None,
    "raid_config": {},
    "reservation": None,
    "resource_class": None,
    "service_step": {},
    "secure_boot": True,
    "shard": "TestShard",
    "runbook": None,
    "states": [
        {
            "href": "http://127.0.0.1:6385/v1/nodes/<NODE_ID>/states",
            "rel": "self",
        },
        {
            "href": "http://127.0.0.1:6385/nodes/<NODE_ID>/states",
            "rel": "bookmark",
        },
    ],
    "target_power_state": None,
    "target_provision_state": None,
    "target_raid_config": {},
    "updated_at": None,
    "uuid": "6d85703a-565d-469a-96ce-30b6de53079d",
}


def _fake_assert(self, session, expected, error_message=None):
    return expected


class TestNode(base.TestCase):
    def test_basic(self):
        sot = node.Node()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('nodes', sot.resources_key)
        self.assertEqual('/nodes', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_instantiate(self):
        sot = node.Node(**FAKE)

        self.assertEqual(FAKE['uuid'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(
            FAKE['automated_clean'], sot.is_automated_clean_enabled
        )
        self.assertEqual(FAKE['boot_mode'], sot.boot_mode)
        self.assertEqual(FAKE['chassis_uuid'], sot.chassis_id)
        self.assertEqual(FAKE['clean_step'], sot.clean_step)
        self.assertEqual(FAKE['conductor_group'], sot.conductor_group)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['driver'], sot.driver)
        self.assertEqual(FAKE['driver_info'], sot.driver_info)
        self.assertEqual(
            FAKE['driver_internal_info'], sot.driver_internal_info
        )
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['firmware_interface'], sot.firmware_interface)
        self.assertEqual(FAKE['instance_info'], sot.instance_info)
        self.assertEqual(FAKE['instance_uuid'], sot.instance_id)
        self.assertEqual(FAKE['console_enabled'], sot.is_console_enabled)
        self.assertEqual(FAKE['maintenance'], sot.is_maintenance)
        self.assertEqual(FAKE['last_error'], sot.last_error)
        self.assertEqual(FAKE['lessee'], sot.lessee)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['maintenance_reason'], sot.maintenance_reason)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['network_interface'], sot.network_interface)
        self.assertEqual(FAKE['owner'], sot.owner)
        self.assertEqual(FAKE['parent_node'], sot.parent_node)
        self.assertEqual(FAKE['ports'], sot.ports)
        self.assertEqual(FAKE['portgroups'], sot.port_groups)
        self.assertEqual(FAKE['power_state'], sot.power_state)
        self.assertEqual(FAKE['properties'], sot.properties)
        self.assertEqual(FAKE['provision_state'], sot.provision_state)
        self.assertEqual(FAKE['raid_config'], sot.raid_config)
        self.assertEqual(FAKE['reservation'], sot.reservation)
        self.assertEqual(FAKE['resource_class'], sot.resource_class)
        self.assertEqual(FAKE['service_step'], sot.service_step)
        self.assertEqual(FAKE['secure_boot'], sot.is_secure_boot)
        self.assertEqual(FAKE['runbook'], sot.runbook)
        self.assertEqual(FAKE['states'], sot.states)
        self.assertEqual(
            FAKE['target_provision_state'], sot.target_provision_state
        )
        self.assertEqual(FAKE['target_power_state'], sot.target_power_state)
        self.assertEqual(FAKE['target_raid_config'], sot.target_raid_config)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)

    def test_normalize_provision_state(self):
        attrs = dict(FAKE, provision_state=None)
        sot = node.Node(**attrs)
        self.assertEqual('available', sot.provision_state)

    @mock.patch.object(node.Node, '_assert_microversion_for', _fake_assert)
    @mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
    def test_list(self):
        self.node = node.Node()
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion=None
        )
        # Set a default, so we don't try and figure out the microversions
        # with additional requests.
        self.session.default_microversion = float(self.node._max_microversion)
        self.session.get.return_value.json.return_value = {'nodes': []}

        result = list(
            self.node.list(
                self.session,
                details=False,
                shard='meow',
                allow_unknown_params=True,
            )
        )
        self.assertEqual(0, len(result))
        self.session.get.assert_called_once_with(
            '/nodes',
            headers={'Accept': 'application/json'},
            params={'shard': 'meow'},
            microversion=float(self.node._max_microversion),
        )


@mock.patch('time.sleep', lambda _t: None)
@mock.patch.object(node.Node, 'fetch', autospec=True)
class TestNodeWaitForProvisionState(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock()

    def test_success(self, mock_fetch):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'manageable'
            self.assertIs(session, self.session)

        mock_fetch.side_effect = _get_side_effect

        node = self.node.wait_for_provision_state(self.session, 'manageable')
        self.assertIs(node, self.node)

    def test_failure(self, mock_fetch):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'deploy failed'
            self.assertIs(session, self.session)

        mock_fetch.side_effect = _get_side_effect

        self.assertRaisesRegex(
            exceptions.ResourceFailure,
            'failure state "deploy failed"',
            self.node.wait_for_provision_state,
            self.session,
            'manageable',
        )

    def test_failure_error(self, mock_fetch):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'error'
            self.assertIs(session, self.session)

        mock_fetch.side_effect = _get_side_effect

        self.assertRaisesRegex(
            exceptions.ResourceFailure,
            'failure state "error"',
            self.node.wait_for_provision_state,
            self.session,
            'manageable',
        )

    def test_enroll_as_failure(self, mock_fetch):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'enroll'
            self.node.last_error = 'power failure'
            self.assertIs(session, self.session)

        mock_fetch.side_effect = _get_side_effect

        self.assertRaisesRegex(
            exceptions.ResourceFailure,
            'failed to verify management credentials',
            self.node.wait_for_provision_state,
            self.session,
            'manageable',
        )

    def test_timeout(self, mock_fetch):
        self.assertRaises(
            exceptions.ResourceTimeout,
            self.node.wait_for_provision_state,
            self.session,
            'manageable',
            timeout=0.001,
        )

    def test_not_abort_on_failed_state(self, mock_fetch):
        def _get_side_effect(_self, session):
            self.node.provision_state = 'deploy failed'
            self.assertIs(session, self.session)

        mock_fetch.side_effect = _get_side_effect

        self.assertRaises(
            exceptions.ResourceTimeout,
            self.node.wait_for_provision_state,
            self.session,
            'manageable',
            timeout=0.001,
            abort_on_failed_state=False,
        )


@mock.patch.object(node.Node, '_assert_microversion_for', _fake_assert)
@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeSetProvisionState(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion=None
        )

    def test_no_arguments(self):
        result = self.node.set_provision_state(self.session, 'active')
        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'active'},
            headers=mock.ANY,
            microversion=None,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_manage(self):
        result = self.node.set_provision_state(self.session, 'manage')
        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'manage'},
            headers=mock.ANY,
            microversion='1.4',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_deploy_with_configdrive(self):
        result = self.node.set_provision_state(
            self.session, 'active', config_drive='abcd'
        )
        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'active', 'configdrive': 'abcd'},
            headers=mock.ANY,
            microversion=None,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_deploy_with_configdrive_as_bytestring(self):
        config_drive = base64.b64encode(b'foo')
        result = self.node.set_provision_state(
            self.session, 'active', config_drive=config_drive
        )
        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'active', 'configdrive': config_drive.decode()},
            headers=mock.ANY,
            microversion=None,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_rebuild_with_configdrive(self):
        result = self.node.set_provision_state(
            self.session, 'rebuild', config_drive='abcd'
        )
        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'rebuild', 'configdrive': 'abcd'},
            headers=mock.ANY,
            microversion='1.35',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_configdrive_as_dict(self):
        for target in ('rebuild', 'active'):
            self.session.put.reset_mock()
            result = self.node.set_provision_state(
                self.session, target, config_drive={'user_data': 'abcd'}
            )
            self.assertIs(result, self.node)
            self.session.put.assert_called_once_with(
                f'nodes/{self.node.id}/states/provision',
                json={'target': target, 'configdrive': {'user_data': 'abcd'}},
                headers=mock.ANY,
                microversion='1.56',
                retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
            )

    def test_deploy_with_deploy_steps(self):
        deploy_steps = [{'interface': 'deploy', 'step': 'upgrade_fw'}]
        result = self.node.set_provision_state(
            self.session, 'active', deploy_steps=deploy_steps
        )

        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'active', 'deploy_steps': deploy_steps},
            headers=mock.ANY,
            microversion='1.69',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_rebuild_with_deploy_steps(self):
        deploy_steps = [{'interface': 'deploy', 'step': 'upgrade_fw'}]
        result = self.node.set_provision_state(
            self.session, 'rebuild', deploy_steps=deploy_steps
        )

        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'rebuild', 'deploy_steps': deploy_steps},
            headers=mock.ANY,
            microversion='1.69',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_provision_state_unhold(self):
        result = self.node.set_provision_state(self.session, 'unhold')

        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'unhold'},
            headers=mock.ANY,
            microversion='1.85',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_provision_state_service(self):
        service_steps = [{'interface': 'deploy', 'step': 'hold'}]
        result = self.node.set_provision_state(
            self.session, 'service', service_steps=service_steps
        )

        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'service', 'service_steps': service_steps},
            headers=mock.ANY,
            microversion='1.87',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_provision_state_clean_runbook(self):
        runbook = 'CUSTOM_AWESOME'
        result = self.node.set_provision_state(
            self.session, 'clean', runbook=runbook
        )

        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'clean', 'runbook': runbook},
            headers=mock.ANY,
            microversion='1.92',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_provision_state_service_runbook(self):
        runbook = 'CUSTOM_AWESOME'
        result = self.node.set_provision_state(
            self.session, 'service', runbook=runbook
        )

        self.assertIs(result, self.node)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/provision',
            json={'target': 'service', 'runbook': runbook},
            headers=mock.ANY,
            microversion='1.92',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )


@mock.patch.object(node.Node, '_translate_response', mock.Mock())
@mock.patch.object(node.Node, '_get_session', lambda self, x: x)
@mock.patch.object(node.Node, 'set_provision_state', autospec=True)
class TestNodeCreate(base.TestCase):
    def setUp(self):
        super().setUp()
        self.new_state = None
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.1'
        self.node = node.Node(driver=FAKE['driver'])

        def _change_state(*args, **kwargs):
            self.node.provision_state = self.new_state

        self.session.post.side_effect = _change_state

    def test_available_old_version(self, mock_prov):
        self.node.provision_state = 'available'
        result = self.node.create(self.session)
        self.assertIs(result, self.node)
        self.session.post.assert_called_once_with(
            mock.ANY,
            json={'driver': FAKE['driver']},
            headers=mock.ANY,
            microversion=self.session.default_microversion,
            params={},
        )
        self.assertFalse(mock_prov.called)

    def test_available_new_version(self, mock_prov):
        self.session.default_microversion = '1.11'
        self.node.provision_state = 'available'

        result = self.node.create(self.session)
        self.assertIs(result, self.node)
        self.session.post.assert_called_once_with(
            mock.ANY,
            json={'driver': FAKE['driver']},
            headers=mock.ANY,
            microversion='1.10',
            params={},
        )
        mock_prov.assert_not_called()

    def test_no_enroll_in_old_version(self, mock_prov):
        self.node.provision_state = 'enroll'
        self.assertRaises(
            exceptions.NotSupported, self.node.create, self.session
        )
        self.assertFalse(self.session.post.called)
        self.assertFalse(mock_prov.called)

    def test_enroll_new_version(self, mock_prov):
        self.session.default_microversion = '1.11'
        self.node.provision_state = 'enroll'
        self.new_state = 'enroll'

        result = self.node.create(self.session)
        self.assertIs(result, self.node)
        self.session.post.assert_called_once_with(
            mock.ANY,
            json={'driver': FAKE['driver']},
            headers=mock.ANY,
            microversion=self.session.default_microversion,
            params={},
        )
        self.assertFalse(mock_prov.called)

    def test_no_manageable_in_old_version(self, mock_prov):
        self.node.provision_state = 'manageable'
        self.assertRaises(
            exceptions.NotSupported, self.node.create, self.session
        )
        self.assertFalse(self.session.post.called)
        self.assertFalse(mock_prov.called)

    def test_manageable_old_version(self, mock_prov):
        self.session.default_microversion = '1.4'
        self.node.provision_state = 'manageable'
        self.new_state = 'available'

        result = self.node.create(self.session)
        self.assertIs(result, self.node)
        self.session.post.assert_called_once_with(
            mock.ANY,
            json={'driver': FAKE['driver']},
            headers=mock.ANY,
            microversion=self.session.default_microversion,
            params={},
        )
        mock_prov.assert_called_once_with(
            self.node, self.session, 'manage', wait=True
        )

    def test_manageable_new_version(self, mock_prov):
        self.session.default_microversion = '1.11'
        self.node.provision_state = 'manageable'
        self.new_state = 'enroll'

        result = self.node.create(self.session)
        self.assertIs(result, self.node)
        self.session.post.assert_called_once_with(
            mock.ANY,
            json={'driver': FAKE['driver']},
            headers=mock.ANY,
            microversion=self.session.default_microversion,
            params={},
        )
        mock_prov.assert_called_once_with(
            self.node, self.session, 'manage', wait=True
        )


@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
@mock.patch.object(node.Node, '_get_session', lambda self, x: x)
class TestNodeVif(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.67'
        self.session.log = mock.Mock()
        self.node = node.Node(
            id='c29db401-b6a7-4530-af8e-20a720dee946', driver=FAKE['driver']
        )
        self.vif_id = '714bdf6d-2386-4b5e-bd0d-bc036f04b1ef'
        self.vif_port_uuid = 'port-uuid'
        self.vif_portgroup_uuid = 'portgroup-uuid'

    def test_attach_vif(self):
        self.assertIsNone(self.node.attach_vif(self.session, self.vif_id))
        self.session.post.assert_called_once_with(
            f'nodes/{self.node.id}/vifs',
            json={'id': self.vif_id},
            headers=mock.ANY,
            microversion='1.67',
            retriable_status_codes=[409, 503],
        )

    def test_attach_vif_no_retries(self):
        self.assertIsNone(
            self.node.attach_vif(
                self.session, self.vif_id, retry_on_conflict=False
            )
        )
        self.session.post.assert_called_once_with(
            f'nodes/{self.node.id}/vifs',
            json={'id': self.vif_id},
            headers=mock.ANY,
            microversion='1.67',
            retriable_status_codes=[503],
        )

    def test_attach_vif_with_port_uuid(self):
        self.assertIsNone(
            self.node.attach_vif(
                self.session, self.vif_id, port_id=self.vif_port_uuid
            )
        )
        self.session.post.assert_called_once_with(
            f'nodes/{self.node.id}/vifs',
            json={'id': self.vif_id, 'port_uuid': self.vif_port_uuid},
            headers=mock.ANY,
            microversion='1.67',
            retriable_status_codes=[409, 503],
        )

    def test_attach_vif_with_portgroup_uuid(self):
        self.assertIsNone(
            self.node.attach_vif(
                self.session,
                self.vif_id,
                port_group_id=self.vif_portgroup_uuid,
            )
        )
        self.session.post.assert_called_once_with(
            f'nodes/{self.node.id}/vifs',
            json={
                'id': self.vif_id,
                'portgroup_uuid': self.vif_portgroup_uuid,
            },
            headers=mock.ANY,
            microversion='1.67',
            retriable_status_codes=[409, 503],
        )

    def test_attach_vif_with_port_uuid_and_portgroup_uuid(self):
        self.assertRaises(
            exceptions.InvalidRequest,
            self.node.attach_vif,
            self.session,
            self.vif_id,
            port_id=self.vif_port_uuid,
            port_group_id=self.vif_portgroup_uuid,
        )

    def test_detach_vif_existing(self):
        self.assertTrue(self.node.detach_vif(self.session, self.vif_id))
        self.session.delete.assert_called_once_with(
            f'nodes/{self.node.id}/vifs/{self.vif_id}',
            headers=mock.ANY,
            microversion='1.67',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_detach_vif_missing(self):
        self.session.delete.return_value.status_code = 400
        self.assertFalse(self.node.detach_vif(self.session, self.vif_id))
        self.session.delete.assert_called_once_with(
            f'nodes/{self.node.id}/vifs/{self.vif_id}',
            headers=mock.ANY,
            microversion='1.67',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_list_vifs(self):
        self.session.get.return_value.json.return_value = {
            'vifs': [
                {'id': '1234'},
                {'id': '5678'},
            ]
        }
        res = self.node.list_vifs(self.session)
        self.assertEqual(['1234', '5678'], res)
        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/vifs',
            headers=mock.ANY,
            microversion='1.67',
        )

    def test_incompatible_microversion(self):
        self.session.default_microversion = '1.1'
        self.assertRaises(
            exceptions.NotSupported,
            self.node.attach_vif,
            self.session,
            self.vif_id,
        )
        self.assertRaises(
            exceptions.NotSupported,
            self.node.detach_vif,
            self.session,
            self.vif_id,
        )
        self.assertRaises(
            exceptions.NotSupported, self.node.list_vifs, self.session
        )

    def test_incompatible_microversion_optional_params(self):
        self.session.default_microversion = '1.28'
        self.assertRaises(
            exceptions.NotSupported,
            self.node.attach_vif,
            self.session,
            self.vif_id,
            port_id=self.vif_port_uuid,
        )
        self.assertRaises(
            exceptions.NotSupported,
            self.node.attach_vif,
            self.session,
            self.vif_id,
            port_group_id=self.vif_portgroup_uuid,
        )


@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
@mock.patch.object(node.Node, '_get_session', lambda self, x: x)
class TestNodeVmedia(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.89'
        self.session.log = mock.Mock()
        self.node = node.Node(
            id='c29db401-b6a7-4530-af8e-20a720dee946', driver=FAKE['driver']
        )
        self.device_type = "CDROM"
        self.image_url = "http://image"

    def test_attach_vmedia(self):
        self.assertIsNone(
            self.node.attach_vmedia(
                self.session, self.device_type, self.image_url
            )
        )
        self.session.post.assert_called_once_with(
            f'nodes/{self.node.id}/vmedia',
            json={
                'device_type': self.device_type,
                'image_url': self.image_url,
            },
            headers=mock.ANY,
            microversion='1.89',
            retriable_status_codes=[409, 503],
        )

    def test_attach_vmedia_no_retries(self):
        self.assertIsNone(
            self.node.attach_vmedia(
                self.session,
                self.device_type,
                self.image_url,
                retry_on_conflict=False,
            )
        )
        self.session.post.assert_called_once_with(
            f'nodes/{self.node.id}/vmedia',
            json={
                'device_type': self.device_type,
                'image_url': self.image_url,
            },
            headers=mock.ANY,
            microversion='1.89',
            retriable_status_codes=[503],
        )

    def test_detach_vmedia_existing(self):
        self.assertIsNone(self.node.detach_vmedia(self.session))
        self.session.delete.assert_called_once_with(
            f'nodes/{self.node.id}/vmedia',
            headers=mock.ANY,
            microversion='1.89',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_detach_vmedia_missing(self):
        self.session.delete.return_value.status_code = 400
        self.assertIsNone(self.node.detach_vmedia(self.session))
        self.session.delete.assert_called_once_with(
            f'nodes/{self.node.id}/vmedia',
            headers=mock.ANY,
            microversion='1.89',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_incompatible_microversion(self):
        self.session.default_microversion = '1.1'
        self.assertRaises(
            exceptions.NotSupported,
            self.node.attach_vmedia,
            self.session,
            self.device_type,
            self.image_url,
        )
        self.assertRaises(
            exceptions.NotSupported,
            self.node.detach_vmedia,
            self.session,
        )


@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
@mock.patch.object(node.Node, '_get_session', lambda self, x: x)
class TestNodeValidate(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.28'
        self.node = node.Node(**FAKE)

    def test_validate_ok(self):
        self.session.get.return_value.json.return_value = {
            'boot': {'result': True},
            'console': {'result': False, 'reason': 'Not configured'},
            'deploy': {'result': True},
            'inspect': {'result': None, 'reason': 'Not supported'},
            'power': {'result': True},
        }
        result = self.node.validate(self.session)
        for iface in ('boot', 'deploy', 'power'):
            self.assertTrue(result[iface].result)
            self.assertFalse(result[iface].reason)
        for iface in ('console', 'inspect'):
            self.assertIsNot(True, result[iface].result)
            self.assertTrue(result[iface].reason)

    def test_validate_failed(self):
        self.session.get.return_value.json.return_value = {
            'boot': {'result': False},
            'console': {'result': False, 'reason': 'Not configured'},
            'deploy': {'result': False, 'reason': 'No deploy for you'},
            'inspect': {'result': None, 'reason': 'Not supported'},
            'power': {'result': True},
        }
        self.assertRaisesRegex(
            exceptions.ValidationException,
            'No deploy for you',
            self.node.validate,
            self.session,
        )

    def test_validate_no_failure(self):
        self.session.get.return_value.json.return_value = {
            'boot': {'result': False},
            'console': {'result': False, 'reason': 'Not configured'},
            'deploy': {'result': False, 'reason': 'No deploy for you'},
            'inspect': {'result': None, 'reason': 'Not supported'},
            'power': {'result': True},
        }
        result = self.node.validate(self.session, required=None)
        self.assertTrue(result['power'].result)
        self.assertFalse(result['power'].reason)
        for iface in ('deploy', 'console', 'inspect'):
            self.assertIsNot(True, result[iface].result)
            self.assertTrue(result[iface].reason)
        # Reason can be empty
        self.assertFalse(result['boot'].result)
        self.assertIsNone(result['boot'].reason)


@mock.patch('time.sleep', lambda _t: None)
@mock.patch.object(node.Node, 'fetch', autospec=True)
class TestNodeWaitForReservation(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.6'
        self.session.log = mock.Mock()
        self.node = node.Node(**FAKE)

    def test_no_reservation(self, mock_fetch):
        self.node.reservation = None
        node = self.node.wait_for_reservation(None)
        self.assertIs(node, self.node)
        self.assertFalse(mock_fetch.called)

    def test_reservation(self, mock_fetch):
        self.node.reservation = 'example.com'

        def _side_effect(node, session):
            if self.node.reservation == 'example.com':
                self.node.reservation = 'example2.com'
            else:
                self.node.reservation = None

        mock_fetch.side_effect = _side_effect
        node = self.node.wait_for_reservation(self.session)
        self.assertIs(node, self.node)
        self.assertEqual(2, mock_fetch.call_count)

    def test_timeout(self, mock_fetch):
        self.node.reservation = 'example.com'

        self.assertRaises(
            exceptions.ResourceTimeout,
            self.node.wait_for_reservation,
            self.session,
            timeout=0.001,
        )
        mock_fetch.assert_called_with(self.node, self.session)


@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeInjectNMI(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = '1.29'
        self.node = node.Node(**FAKE)

    def test_inject_nmi(self):
        self.node.inject_nmi(self.session)
        self.session.put.assert_called_once_with(
            'nodes/{}/management/inject_nmi'.format(FAKE['uuid']),
            json={},
            headers=mock.ANY,
            microversion='1.29',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_incompatible_microversion(self):
        self.session.default_microversion = '1.28'
        self.assertRaises(
            exceptions.NotSupported,
            self.node.inject_nmi,
            self.session,
        )


@mock.patch.object(node.Node, '_assert_microversion_for', _fake_assert)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeSetPowerState(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion=None
        )

    def test_power_on(self):
        self.node.set_power_state(self.session, 'power on')
        self.session.put.assert_called_once_with(
            'nodes/{}/states/power'.format(FAKE['uuid']),
            json={'target': 'power on'},
            headers=mock.ANY,
            microversion=None,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_soft_power_on(self):
        self.node.set_power_state(self.session, 'soft power off')
        self.session.put.assert_called_once_with(
            'nodes/{}/states/power'.format(FAKE['uuid']),
            json={'target': 'soft power off'},
            headers=mock.ANY,
            microversion='1.27',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )


@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
@mock.patch.object(node.Node, '_translate_response', mock.Mock())
@mock.patch.object(node.Node, '_get_session', lambda self, x: x)
class TestNodeMaintenance(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node.existing(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter,
            default_microversion='1.1',
            retriable_status_codes=None,
        )

    def test_set(self):
        self.node.set_maintenance(self.session)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json={'reason': None},
            headers=mock.ANY,
            microversion=mock.ANY,
        )

    def test_set_with_reason(self):
        self.node.set_maintenance(self.session, 'No work on Monday')
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json={'reason': 'No work on Monday'},
            headers=mock.ANY,
            microversion=mock.ANY,
        )

    def test_unset(self):
        self.node.unset_maintenance(self.session)
        self.session.delete.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json=None,
            headers=mock.ANY,
            microversion=mock.ANY,
        )

    def test_set_via_update(self):
        self.node.is_maintenance = True
        self.node.commit(self.session)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json={'reason': None},
            headers=mock.ANY,
            microversion=mock.ANY,
        )

        self.assertFalse(self.session.patch.called)

    def test_set_with_reason_via_update(self):
        self.node.is_maintenance = True
        self.node.maintenance_reason = 'No work on Monday'
        self.node.commit(self.session)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json={'reason': 'No work on Monday'},
            headers=mock.ANY,
            microversion=mock.ANY,
        )
        self.assertFalse(self.session.patch.called)

    def test_set_with_other_fields(self):
        self.node.is_maintenance = True
        self.node.name = 'lazy-3000'
        self.node.commit(self.session)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json={'reason': None},
            headers=mock.ANY,
            microversion=mock.ANY,
        )

        self.session.patch.assert_called_once_with(
            f'nodes/{self.node.id}',
            json=[{'path': '/name', 'op': 'replace', 'value': 'lazy-3000'}],
            headers=mock.ANY,
            microversion=mock.ANY,
        )

    def test_set_with_reason_and_other_fields(self):
        self.node.is_maintenance = True
        self.node.maintenance_reason = 'No work on Monday'
        self.node.name = 'lazy-3000'
        self.node.commit(self.session)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json={'reason': 'No work on Monday'},
            headers=mock.ANY,
            microversion=mock.ANY,
        )

        self.session.patch.assert_called_once_with(
            f'nodes/{self.node.id}',
            json=[{'path': '/name', 'op': 'replace', 'value': 'lazy-3000'}],
            headers=mock.ANY,
            microversion=mock.ANY,
        )

    def test_no_reason_without_maintenance(self):
        self.node.maintenance_reason = 'Can I?'
        self.assertRaises(ValueError, self.node.commit, self.session)
        self.assertFalse(self.session.put.called)
        self.assertFalse(self.session.patch.called)

    def test_set_unset_maintenance(self):
        self.node.is_maintenance = True
        self.node.maintenance_reason = 'No work on Monday'
        self.node.commit(self.session)

        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json={'reason': 'No work on Monday'},
            headers=mock.ANY,
            microversion=mock.ANY,
        )

        self.node.is_maintenance = False
        self.node.commit(self.session)
        self.assertIsNone(self.node.maintenance_reason)

        self.session.delete.assert_called_once_with(
            f'nodes/{self.node.id}/maintenance',
            json=None,
            headers=mock.ANY,
            microversion=mock.ANY,
        )


@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeBootDevice(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion='1.1'
        )

    def test_get_boot_device(self):
        self.node.get_boot_device(self.session)
        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/management/boot_device',
            headers=mock.ANY,
            microversion=mock.ANY,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_boot_device(self):
        self.node.set_boot_device(self.session, 'pxe', persistent=False)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/management/boot_device',
            json={'boot_device': 'pxe', 'persistent': False},
            headers=mock.ANY,
            microversion=mock.ANY,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_get_supported_boot_devices(self):
        self.node.get_supported_boot_devices(self.session)
        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/management/boot_device/supported',
            headers=mock.ANY,
            microversion=mock.ANY,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )


@mock.patch.object(utils, 'pick_microversion', lambda session, v: v)
@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeSetBootMode(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion='1.1'
        )

    def test_node_set_boot_mode(self):
        self.node.set_boot_mode(self.session, 'uefi')
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/boot_mode',
            json={'target': 'uefi'},
            headers=mock.ANY,
            microversion=mock.ANY,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_node_set_boot_mode_invalid_mode(self):
        self.assertRaises(
            ValueError, self.node.set_boot_mode, self.session, 'invalid-efi'
        )


@mock.patch.object(utils, 'pick_microversion', lambda session, v: v)
@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeSetSecureBoot(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion='1.1'
        )

    def test_node_set_secure_boot(self):
        self.node.set_secure_boot(self.session, True)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/secure_boot',
            json={'target': True},
            headers=mock.ANY,
            microversion=mock.ANY,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_node_set_secure_boot_invalid_none(self):
        self.assertRaises(
            ValueError, self.node.set_secure_boot, self.session, None
        )


@mock.patch.object(utils, 'pick_microversion', lambda session, v: v)
@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeTraits(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion='1.37'
        )
        self.session.log = mock.Mock()

    def test_node_add_trait(self):
        self.node.add_trait(self.session, 'CUSTOM_FAKE')
        self.session.put.assert_called_once_with(
            'nodes/{}/traits/{}'.format(self.node.id, 'CUSTOM_FAKE'),
            json=None,
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_remove_trait(self):
        self.assertTrue(self.node.remove_trait(self.session, 'CUSTOM_FAKE'))
        self.session.delete.assert_called_once_with(
            'nodes/{}/traits/{}'.format(self.node.id, 'CUSTOM_FAKE'),
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_remove_trait_missing(self):
        self.session.delete.return_value.status_code = 400
        self.assertFalse(
            self.node.remove_trait(self.session, 'CUSTOM_MISSING')
        )
        self.session.delete.assert_called_once_with(
            'nodes/{}/traits/{}'.format(self.node.id, 'CUSTOM_MISSING'),
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_traits(self):
        traits = ['CUSTOM_FAKE', 'CUSTOM_REAL', 'CUSTOM_MISSING']
        self.node.set_traits(self.session, traits)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/traits',
            json={'traits': ['CUSTOM_FAKE', 'CUSTOM_REAL', 'CUSTOM_MISSING']},
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )


@mock.patch.object(node.Node, '_assert_microversion_for', _fake_assert)
@mock.patch.object(resource.Resource, 'patch', autospec=True)
class TestNodePatch(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion=None
        )
        self.session.log = mock.Mock()

    def test_node_patch(self, mock_patch):
        patch = {'path': 'test'}
        self.node.patch(self.session, patch=patch)
        mock_patch.assert_called_once()
        kwargs = mock_patch.call_args[1]
        self.assertEqual(kwargs['patch'], {'path': 'test'})

    @mock.patch.object(resource.Resource, '_prepare_request', autospec=True)
    @mock.patch.object(resource.Resource, '_commit', autospec=True)
    def test_node_patch_reset_interfaces(
        self, mock__commit, mock_prepreq, mock_patch
    ):
        patch = {'path': 'test'}
        self.node.patch(
            self.session,
            patch=patch,
            retry_on_conflict=True,
            reset_interfaces=True,
        )
        mock_prepreq.assert_called_once()
        prepreq_kwargs = mock_prepreq.call_args[1]
        self.assertEqual(
            prepreq_kwargs['params'], [('reset_interfaces', True)]
        )
        mock__commit.assert_called_once()
        commit_args = mock__commit.call_args[0]
        commit_kwargs = mock__commit.call_args[1]
        self.assertIn('1.45', commit_args)
        self.assertEqual(commit_kwargs['retry_on_conflict'], True)
        mock_patch.assert_not_called()


@mock.patch('time.sleep', lambda _t: None)
@mock.patch.object(node.Node, 'fetch', autospec=True)
class TestNodeWaitForPowerState(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock()

    def test_success(self, mock_fetch):
        self.node.power_state = 'power on'

        def _get_side_effect(_self, session):
            self.node.power_state = 'power off'
            self.assertIs(session, self.session)

        mock_fetch.side_effect = _get_side_effect

        node = self.node.wait_for_power_state(self.session, 'power off')
        self.assertIs(node, self.node)

    def test_timeout(self, mock_fetch):
        self.node.power_state = 'power on'
        self.assertRaises(
            exceptions.ResourceTimeout,
            self.node.wait_for_power_state,
            self.session,
            'power off',
            timeout=0.001,
        )


@mock.patch.object(utils, 'pick_microversion', lambda session, v: v)
@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodePassthru:
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = node.Mock(
            spec=adapter.Adapter, default_microversion='1.37'
        )
        self.session.log = mock.Mock()

    def test_get_passthru(self):
        self.node.call_vendor_passthru(self.session, "GET", "test_method")
        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/vendor_passthru?method=test_method',
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_post_passthru(self):
        self.node.call_vendor_passthru(self.session, "POST", "test_method")
        self.session.post.assert_called_once_with(
            f'nodes/{self.node.id}/vendor_passthru?method=test_method',
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_put_passthru(self):
        self.node.call_vendor_passthru(self.session, "PUT", "test_method")
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/vendor_passthru?method=test_method',
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_delete_passthru(self):
        self.node.call_vendor_passthru(self.session, "DELETE", "test_method")
        self.session.delete.assert_called_once_with(
            f'nodes/{self.node.id}/vendor_passthru?method=test_method',
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_list_passthru(self):
        self.node.list_vendor_passthru(self.session)
        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/vendor_passthru/methods',
            headers=mock.ANY,
            microversion='1.37',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )


@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeConsole(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter,
            default_microversion='1.1',
        )

    def test_get_console(self):
        self.node.get_console(self.session)
        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/states/console',
            headers=mock.ANY,
            microversion=mock.ANY,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_console_mode(self):
        self.node.set_console_mode(self.session, True)
        self.session.put.assert_called_once_with(
            f'nodes/{self.node.id}/states/console',
            json={'enabled': True},
            headers=mock.ANY,
            microversion=mock.ANY,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

    def test_set_console_mode_invalid_enabled(self):
        self.assertRaises(
            ValueError,
            self.node.set_console_mode,
            self.session,
            'true',  # not a bool
        )


@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeInventory(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter,
            default_microversion='1.81',
        )

    def test_get_inventory(self):
        node_inventory = {
            'inventory': {
                'memory': {'physical_mb': 3072},
                'cpu': {
                    'count': 1,
                    'model_name': 'qemu64',
                    'architecture': 'x86_64',
                },
                'disks': [{'name': 'testvm1.qcow2', 'size': 11811160064}],
                'interfaces': [{'mac_address': '52:54:00:c7:02:45'}],
                'system_vendor': {
                    'product_name': 'testvm1',
                    'manufacturer': 'Sushy Emulator',
                },
                'boot': {'current_boot_mode': 'uefi'},
            },
            'plugin_data': {'fake_plugin_data'},
        }
        self.session.get.return_value.json.return_value = node_inventory

        res = self.node.get_node_inventory(self.session, self.node.id)
        self.assertEqual(node_inventory, res)

        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/inventory',
            headers=mock.ANY,
            microversion='1.81',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )


@mock.patch.object(node.Node, 'fetch', lambda self, session: self)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestNodeFirmware(base.TestCase):
    def setUp(self):
        super().setUp()
        self.node = node.Node(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter,
            default_microversion='1.86',
        )

    def test_list_firmware(self):
        node_firmware = {
            "firmware": [
                {
                    "created_at": "2016-08-18T22:28:49.653974+00:00",
                    "updated_at": "2016-08-18T22:28:49.653974+00:00",
                    "component": "BMC",
                    "initial_version": "v1.0.0",
                    "current_version": "v1.2.0",
                    "last_version_flashed": "v1.2.0",
                },
                {
                    "created_at": "2016-08-18T22:28:49.653974+00:00",
                    "updated_at": "2016-08-18T22:28:49.653974+00:00",
                    "component": "BIOS",
                    "initial_version": "v1.0.0",
                    "current_version": "v1.1.5",
                    "last_version_flashed": "v1.1.5",
                },
            ]
        }
        self.session.get.return_value.json.return_value = node_firmware

        res = self.node.list_firmware(self.session)
        self.assertEqual(node_firmware, res)

        self.session.get.assert_called_once_with(
            f'nodes/{self.node.id}/firmware',
            headers=mock.ANY,
            microversion='1.86',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )
