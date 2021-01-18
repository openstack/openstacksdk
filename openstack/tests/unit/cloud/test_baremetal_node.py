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

"""
test_baremetal_node
----------------------------------

Tests for baremetal node related operations
"""

import uuid

from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

from openstack.cloud import exc
from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestBaremetalNode(base.IronicTestCase):

    def setUp(self):
        super(TestBaremetalNode, self).setUp()
        self.fake_baremetal_node = fakes.make_fake_machine(
            self.name, self.uuid)
        # TODO(TheJulia): Some tests below have fake ports,
        # since they are required in some processes. Lets refactor
        # them at some point to use self.fake_baremetal_port.
        self.fake_baremetal_port = fakes.make_fake_port(
            '00:01:02:03:04:05',
            node_id=self.uuid)

    def test_list_machines(self):
        fake_baremetal_two = fakes.make_fake_machine('two', str(uuid.uuid4()))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='nodes'),
                 json={'nodes': [self.fake_baremetal_node,
                                 fake_baremetal_two]}),
        ])

        machines = self.cloud.list_machines()
        self.assertEqual(2, len(machines))
        self.assertSubdict(self.fake_baremetal_node, machines[0])
        self.assertSubdict(fake_baremetal_two, machines[1])
        self.assert_calls()

    def test_get_machine(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        machine = self.cloud.get_machine(self.fake_baremetal_node['uuid'])
        self.assertEqual(machine['uuid'],
                         self.fake_baremetal_node['uuid'])
        self.assert_calls()

    def test_get_machine_by_mac(self):
        mac_address = '00:01:02:03:04:05'
        node_uuid = self.fake_baremetal_node['uuid']
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='ports',
                     append=['detail'],
                     qs_elements=['address=%s' % mac_address]),
                 json={'ports': [{'address': mac_address,
                                  'node_uuid': node_uuid}]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        machine = self.cloud.get_machine_by_mac(mac_address)
        self.assertEqual(machine['uuid'],
                         self.fake_baremetal_node['uuid'])
        self.assert_calls()

    def test_validate_machine(self):
        # NOTE(TheJulia): Note: These are only the interfaces
        # that are validated, and all must be true for an
        # exception to not be raised.
        validate_return = {
            'boot': {
                'result': True,
            },
            'deploy': {
                'result': True,
            },
            'management': {
                'result': True,
            },
            'power': {
                'result': True,
            },
            'foo': {
                'result': False,
            }}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid'],
                             'validate']),
                 json=validate_return),
        ])
        self.cloud.validate_machine(self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_validate_machine_not_for_deploy(self):
        validate_return = {
            'deploy': {
                'result': False,
                'reason': 'Not ready',
            },
            'power': {
                'result': True,
            },
            'foo': {
                'result': False,
            }}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid'],
                             'validate']),
                 json=validate_return),
        ])
        self.cloud.validate_machine(self.fake_baremetal_node['uuid'],
                                    for_deploy=False)

        self.assert_calls()

    def test_deprecated_validate_node(self):
        validate_return = {
            'deploy': {
                'result': True,
            },
            'power': {
                'result': True,
            },
            'foo': {
                'result': False,
            }}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid'],
                             'validate']),
                 json=validate_return),
        ])
        self.cloud.validate_node(self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_validate_machine_raises_exception(self):
        validate_return = {
            'deploy': {
                'result': False,
                'reason': 'error!',
            },
            'power': {
                'result': True,
                'reason': None,
            },
            'foo': {
                'result': True
            }}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid'],
                             'validate']),
                 json=validate_return),
        ])
        self.assertRaises(
            exceptions.ValidationException,
            self.cloud.validate_machine,
            self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_patch_machine(self):
        test_patch = [{
            'op': 'remove',
            'path': '/instance_info'}]
        self.fake_baremetal_node['instance_info'] = {}
        self.register_uris([
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node,
                 validate=dict(json=test_patch)),
        ])
        result = self.cloud.patch_machine(
            self.fake_baremetal_node['uuid'], test_patch)
        self.assertEqual(self.fake_baremetal_node['uuid'], result['uuid'])

        self.assert_calls()

    def test_set_node_instance_info(self):
        test_patch = [{
            'op': 'add',
            'path': '/foo',
            'value': 'bar'}]
        self.register_uris([
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node,
                 validate=dict(json=test_patch)),
        ])
        self.cloud.set_node_instance_info(
            self.fake_baremetal_node['uuid'], test_patch)

        self.assert_calls()

    def test_purge_node_instance_info(self):
        test_patch = [{
            'op': 'remove',
            'path': '/instance_info'}]
        self.fake_baremetal_node['instance_info'] = {}
        self.register_uris([
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node,
                 validate=dict(json=test_patch)),
        ])
        self.cloud.purge_node_instance_info(
            self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_inspect_machine_fail_active(self):
        self.fake_baremetal_node['provision_state'] = 'active'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.inspect_machine,
            self.fake_baremetal_node['uuid'],
            wait=True,
            timeout=1)

        self.assert_calls()

    def test_inspect_machine_fail_associated(self):
        self.fake_baremetal_node['provision_state'] = 'available'
        self.fake_baremetal_node['instance_uuid'] = '1234'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])
        self.assertRaisesRegex(
            exc.OpenStackCloudException,
            'associated with an instance',
            self.cloud.inspect_machine,
            self.fake_baremetal_node['uuid'],
            wait=True,
            timeout=1)

        self.assert_calls()

    def test_inspect_machine_failed(self):
        inspecting_node = self.fake_baremetal_node.copy()
        self.fake_baremetal_node['provision_state'] = 'inspect failed'
        self.fake_baremetal_node['last_error'] = 'kaboom!'
        inspecting_node['provision_state'] = 'inspecting'
        finished_node = self.fake_baremetal_node.copy()
        finished_node['provision_state'] = 'manageable'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'inspect'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=inspecting_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=finished_node),
        ])

        self.cloud.inspect_machine(self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_inspect_machine_manageable(self):
        self.fake_baremetal_node['provision_state'] = 'manageable'
        inspecting_node = self.fake_baremetal_node.copy()
        inspecting_node['provision_state'] = 'inspecting'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'inspect'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=inspecting_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
        ])
        self.cloud.inspect_machine(self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_inspect_machine_available(self):
        available_node = self.fake_baremetal_node.copy()
        available_node['provision_state'] = 'available'
        manageable_node = self.fake_baremetal_node.copy()
        manageable_node['provision_state'] = 'manageable'

        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'manage'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=manageable_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'inspect'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=manageable_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'provide'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
        ])
        self.cloud.inspect_machine(self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_inspect_machine_available_wait(self):
        available_node = self.fake_baremetal_node.copy()
        available_node['provision_state'] = 'available'
        manageable_node = self.fake_baremetal_node.copy()
        manageable_node['provision_state'] = 'manageable'
        inspecting_node = self.fake_baremetal_node.copy()
        inspecting_node['provision_state'] = 'inspecting'

        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'manage'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=manageable_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'inspect'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=inspecting_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=manageable_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'provide'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
        ])
        self.cloud.inspect_machine(
            self.fake_baremetal_node['uuid'], wait=True, timeout=1)

        self.assert_calls()

    def test_inspect_machine_wait(self):
        self.fake_baremetal_node['provision_state'] = 'manageable'
        inspecting_node = self.fake_baremetal_node.copy()
        inspecting_node['provision_state'] = 'inspecting'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'inspect'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=inspecting_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=inspecting_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
        ])
        self.cloud.inspect_machine(
            self.fake_baremetal_node['uuid'], wait=True, timeout=1)

        self.assert_calls()

    def test_inspect_machine_inspect_failed(self):
        self.fake_baremetal_node['provision_state'] = 'manageable'
        inspecting_node = self.fake_baremetal_node.copy()
        inspecting_node['provision_state'] = 'inspecting'
        inspect_fail_node = self.fake_baremetal_node.copy()
        inspect_fail_node['provision_state'] = 'inspect failed'
        inspect_fail_node['last_error'] = 'Earth Imploded'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'inspect'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=inspecting_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=inspect_fail_node),
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.inspect_machine,
                          self.fake_baremetal_node['uuid'],
                          wait=True, timeout=1)

        self.assert_calls()

    def test_set_machine_maintenace_state(self):
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'maintenance']),
                validate=dict(json={'reason': 'no reason'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
        ])
        self.cloud.set_machine_maintenance_state(
            self.fake_baremetal_node['uuid'], True, reason='no reason')

        self.assert_calls()

    def test_set_machine_maintenace_state_false(self):
        self.register_uris([
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'maintenance'])),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
        ])
        self.cloud.set_machine_maintenance_state(
            self.fake_baremetal_node['uuid'], False)

        self.assert_calls

    def test_remove_machine_from_maintenance(self):
        self.register_uris([
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'maintenance'])),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
        ])
        self.cloud.remove_machine_from_maintenance(
            self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_set_machine_power_on(self):
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'power']),
                validate=dict(json={'target': 'power on'})),
        ])
        return_value = self.cloud.set_machine_power_on(
            self.fake_baremetal_node['uuid'])
        self.assertIsNone(return_value)

        self.assert_calls()

    def test_set_machine_power_on_with_retires(self):
        # NOTE(TheJulia): This logic ends up testing power on/off and reboot
        # as they all utilize the same helper method.
        self.register_uris([
            dict(
                method='PUT',
                status_code=503,
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'power']),
                validate=dict(json={'target': 'power on'})),
            dict(
                method='PUT',
                status_code=409,
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'power']),
                validate=dict(json={'target': 'power on'})),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'power']),
                validate=dict(json={'target': 'power on'})),
        ])
        return_value = self.cloud.set_machine_power_on(
            self.fake_baremetal_node['uuid'])
        self.assertIsNone(return_value)

        self.assert_calls()

    def test_set_machine_power_off(self):
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'power']),
                validate=dict(json={'target': 'power off'})),
        ])
        return_value = self.cloud.set_machine_power_off(
            self.fake_baremetal_node['uuid'])
        self.assertIsNone(return_value)

        self.assert_calls()

    def test_set_machine_power_reboot(self):
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'power']),
                validate=dict(json={'target': 'rebooting'})),
        ])
        return_value = self.cloud.set_machine_power_reboot(
            self.fake_baremetal_node['uuid'])
        self.assertIsNone(return_value)

        self.assert_calls()

    def test_set_machine_power_reboot_failure(self):
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'power']),
                status_code=400,
                json={'error': 'invalid'},
                validate=dict(json={'target': 'rebooting'})),
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.set_machine_power_reboot,
                          self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_node_set_provision_state(self):
        deploy_node = self.fake_baremetal_node.copy()
        deploy_node['provision_state'] = 'deploying'
        active_node = self.fake_baremetal_node.copy()
        active_node['provision_state'] = 'active'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active',
                                    'configdrive': 'http://host/file'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])
        result = self.cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'active',
            configdrive='http://host/file')
        self.assertEqual(self.fake_baremetal_node['uuid'], result['uuid'])

        self.assert_calls()

    def test_node_set_provision_state_with_retries(self):
        deploy_node = self.fake_baremetal_node.copy()
        deploy_node['provision_state'] = 'deploying'
        active_node = self.fake_baremetal_node.copy()
        active_node['provision_state'] = 'active'
        self.register_uris([
            dict(
                method='PUT',
                status_code=409,
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active',
                                    'configdrive': 'http://host/file'})),
            dict(
                method='PUT',
                status_code=503,
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active',
                                    'configdrive': 'http://host/file'})),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active',
                                    'configdrive': 'http://host/file'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])
        self.cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'active',
            configdrive='http://host/file')

        self.assert_calls()

    def test_node_set_provision_state_wait_timeout(self):
        deploy_node = self.fake_baremetal_node.copy()
        deploy_node['provision_state'] = 'deploying'
        active_node = self.fake_baremetal_node.copy()
        active_node['provision_state'] = 'active'
        self.fake_baremetal_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=deploy_node),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=active_node),
        ])
        return_value = self.cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'active',
            wait=True)

        self.assertSubdict(active_node, return_value)
        self.assert_calls()

    def test_node_set_provision_state_wait_timeout_fails(self):
        # Intentionally time out.
        self.fake_baremetal_node['provision_state'] = 'deploy wait'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.node_set_provision_state,
            self.fake_baremetal_node['uuid'],
            'active',
            wait=True,
            timeout=0.001)

        self.assert_calls()

    def test_node_set_provision_state_wait_success(self):
        self.fake_baremetal_node['provision_state'] = 'active'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        return_value = self.cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'active',
            wait=True)

        self.assertSubdict(self.fake_baremetal_node, return_value)
        self.assert_calls()

    def test_node_set_provision_state_wait_failure_cases(self):
        self.fake_baremetal_node['provision_state'] = 'foo failed'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.node_set_provision_state,
            self.fake_baremetal_node['uuid'],
            'active',
            wait=True,
            timeout=300)

        self.assert_calls()

    def test_node_set_provision_state_wait_provide(self):
        self.fake_baremetal_node['provision_state'] = 'manageable'
        available_node = self.fake_baremetal_node.copy()
        available_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'provide'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=available_node),
        ])
        return_value = self.cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'provide',
            wait=True)

        self.assertSubdict(available_node, return_value)
        self.assert_calls()

    def test_wait_for_baremetal_node_lock_locked(self):
        self.fake_baremetal_node['reservation'] = 'conductor0'
        unlocked_node = self.fake_baremetal_node.copy()
        unlocked_node['reservation'] = None
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=unlocked_node),
        ])
        self.assertIsNone(
            self.cloud.wait_for_baremetal_node_lock(
                self.fake_baremetal_node,
                timeout=1))

        self.assert_calls()

    def test_wait_for_baremetal_node_lock_not_locked(self):
        self.fake_baremetal_node['reservation'] = None
        self.assertIsNone(
            self.cloud.wait_for_baremetal_node_lock(
                self.fake_baremetal_node,
                timeout=1))

        # NOTE(dtantsur): service discovery apparently requires 3 calls
        self.assertEqual(3, len(self.adapter.request_history))

    def test_wait_for_baremetal_node_lock_timeout(self):
        self.fake_baremetal_node['reservation'] = 'conductor0'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.wait_for_baremetal_node_lock,
            self.fake_baremetal_node,
            timeout=0.001)

        self.assert_calls()

    def test_activate_node(self):
        self.fake_baremetal_node['provision_state'] = 'active'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'active',
                                    'configdrive': 'http://host/file'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])
        return_value = self.cloud.activate_node(
            self.fake_baremetal_node['uuid'],
            configdrive='http://host/file',
            wait=True)

        self.assertIsNone(return_value)
        self.assert_calls()

    def test_deactivate_node(self):
        self.fake_baremetal_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'deleted'})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])
        return_value = self.cloud.deactivate_node(
            self.fake_baremetal_node['uuid'],
            wait=True)

        self.assertIsNone(return_value)
        self.assert_calls()

    def test_register_machine(self):
        mac_address = '00:01:02:03:04:05'
        nics = [{'mac': mac_address}]
        node_uuid = self.fake_baremetal_node['uuid']
        # TODO(TheJulia): There is a lot of duplication
        # in testing creation. Surely this hsould be a helper
        # or something. We should fix this.
        node_to_post = {
            'chassis_uuid': None,
            'driver': None,
            'driver_info': None,
            'name': self.fake_baremetal_node['name'],
            'properties': None,
            'uuid': node_uuid}
        self.fake_baremetal_node['provision_state'] = 'available'
        if 'provision_state' in node_to_post:
            node_to_post.pop('provision_state')
        self.register_uris([
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes'),
                json=self.fake_baremetal_node,
                validate=dict(json=node_to_post)),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='ports'),
                validate=dict(json={'address': mac_address,
                                    'node_uuid': node_uuid}),
                json=self.fake_baremetal_port),
        ])
        return_value = self.cloud.register_machine(nics, **node_to_post)

        self.assertDictEqual(self.fake_baremetal_node, return_value)
        self.assert_calls()

    # TODO(TheJulia): We need to de-duplicate these tests.
    # Possibly a dedicated class, although we should do it
    # then as we may find differences that need to be
    # accounted for newer microversions.
    def test_register_machine_enroll(self):
        mac_address = '00:01:02:03:04:05'
        nics = [{'mac': mac_address}]
        node_uuid = self.fake_baremetal_node['uuid']
        node_to_post = {
            'chassis_uuid': None,
            'driver': None,
            'driver_info': None,
            'name': self.fake_baremetal_node['name'],
            'properties': None,
            'uuid': node_uuid}
        self.fake_baremetal_node['provision_state'] = 'enroll'
        manageable_node = self.fake_baremetal_node.copy()
        manageable_node['provision_state'] = 'manageable'
        available_node = self.fake_baremetal_node.copy()
        available_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes'),
                validate=dict(json=node_to_post),
                json=self.fake_baremetal_node),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='ports'),
                validate=dict(json={'address': mac_address,
                                    'node_uuid': node_uuid}),
                json=self.fake_baremetal_port),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'manage'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=manageable_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=manageable_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'provide'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
        ])
        # NOTE(When we migrate to a newer microversion, this test
        # may require revision. It was written for microversion
        # ?1.13?, which accidently got reverted to 1.6 at one
        # point during code being refactored soon after the
        # change landed. Presently, with the lock at 1.6,
        # this code is never used in the current code path.
        return_value = self.cloud.register_machine(nics, **node_to_post)

        self.assertSubdict(available_node, return_value)
        self.assert_calls()

    def test_register_machine_enroll_wait(self):
        mac_address = self.fake_baremetal_port
        nics = [{'mac': mac_address}]
        node_uuid = self.fake_baremetal_node['uuid']
        node_to_post = {
            'chassis_uuid': None,
            'driver': None,
            'driver_info': None,
            'name': self.fake_baremetal_node['name'],
            'properties': None,
            'uuid': node_uuid}
        self.fake_baremetal_node['provision_state'] = 'enroll'
        manageable_node = self.fake_baremetal_node.copy()
        manageable_node['provision_state'] = 'manageable'
        available_node = self.fake_baremetal_node.copy()
        available_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes'),
                validate=dict(json=node_to_post),
                json=self.fake_baremetal_node),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='ports'),
                validate=dict(json={'address': mac_address,
                                    'node_uuid': node_uuid}),
                json=self.fake_baremetal_port),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'manage'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=manageable_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'provide'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=available_node),
        ])
        return_value = self.cloud.register_machine(
            nics, wait=True, **node_to_post)

        self.assertSubdict(available_node, return_value)
        self.assert_calls()

    def test_register_machine_enroll_failure(self):
        mac_address = '00:01:02:03:04:05'
        nics = [{'mac': mac_address}]
        node_uuid = self.fake_baremetal_node['uuid']
        node_to_post = {
            'chassis_uuid': None,
            'driver': None,
            'driver_info': None,
            'name': self.fake_baremetal_node['name'],
            'properties': None,
            'uuid': node_uuid}
        self.fake_baremetal_node['provision_state'] = 'enroll'
        failed_node = self.fake_baremetal_node.copy()
        failed_node['reservation'] = 'conductor0'
        failed_node['provision_state'] = 'verifying'
        failed_node['last_error'] = 'kaboom!'
        self.register_uris([
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes'),
                json=self.fake_baremetal_node,
                validate=dict(json=node_to_post)),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='ports'),
                validate=dict(json={'address': mac_address,
                                    'node_uuid': node_uuid}),
                json=self.fake_baremetal_port),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'manage'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=failed_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=failed_node),
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.register_machine,
            nics,
            **node_to_post)
        self.assert_calls()

    def test_register_machine_enroll_timeout(self):
        mac_address = '00:01:02:03:04:05'
        nics = [{'mac': mac_address}]
        node_uuid = self.fake_baremetal_node['uuid']
        node_to_post = {
            'chassis_uuid': None,
            'driver': None,
            'driver_info': None,
            'name': self.fake_baremetal_node['name'],
            'properties': None,
            'uuid': node_uuid}
        self.fake_baremetal_node['provision_state'] = 'enroll'
        busy_node = self.fake_baremetal_node.copy()
        busy_node['reservation'] = 'conductor0'
        busy_node['provision_state'] = 'verifying'
        self.register_uris([
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes'),
                json=self.fake_baremetal_node,
                validate=dict(json=node_to_post)),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='ports'),
                validate=dict(json={'address': mac_address,
                                    'node_uuid': node_uuid}),
                json=self.fake_baremetal_port),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'manage'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=busy_node),
        ])
        # NOTE(TheJulia): This test shortcircuits the timeout loop
        # such that it executes only once. The very last returned
        # state to the API is essentially a busy state that we
        # want to block on until it has cleared.
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.register_machine,
            nics,
            timeout=0.001,
            lock_timeout=0.001,
            **node_to_post)
        self.assert_calls()

    def test_register_machine_enroll_timeout_wait(self):
        mac_address = '00:01:02:03:04:05'
        nics = [{'mac': mac_address}]
        node_uuid = self.fake_baremetal_node['uuid']
        node_to_post = {
            'chassis_uuid': None,
            'driver': None,
            'driver_info': None,
            'name': self.fake_baremetal_node['name'],
            'properties': None,
            'uuid': node_uuid}
        self.fake_baremetal_node['provision_state'] = 'enroll'
        self.register_uris([
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes'),
                json=self.fake_baremetal_node,
                validate=dict(json=node_to_post)),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='ports'),
                validate=dict(json={'address': mac_address,
                                    'node_uuid': node_uuid}),
                json=self.fake_baremetal_port),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='PUT',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'],
                            'states', 'provision']),
                validate=dict(json={'target': 'manage'})),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.register_machine,
            nics,
            wait=True,
            timeout=0.001,
            **node_to_post)
        self.assert_calls()

    def test_register_machine_port_create_failed(self):
        mac_address = '00:01:02:03:04:05'
        nics = [{'mac': mac_address}]
        node_uuid = self.fake_baremetal_node['uuid']
        node_to_post = {
            'chassis_uuid': None,
            'driver': None,
            'driver_info': None,
            'name': self.fake_baremetal_node['name'],
            'properties': None,
            'uuid': node_uuid}
        self.fake_baremetal_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes'),
                json=self.fake_baremetal_node,
                validate=dict(json=node_to_post)),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='ports'),
                status_code=400,
                json={'error': 'invalid'},
                validate=dict(json={'address': mac_address,
                                    'node_uuid': node_uuid})),
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']])),
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.register_machine,
                          nics, **node_to_post)

        self.assert_calls()

    def test_unregister_machine(self):
        mac_address = self.fake_baremetal_port['address']
        nics = [{'mac': mac_address}]
        port_uuid = self.fake_baremetal_port['uuid']
        # NOTE(TheJulia): The two values below should be the same.
        port_node_uuid = self.fake_baremetal_port['node_uuid']
        self.fake_baremetal_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='ports',
                    qs_elements=['address=%s' % mac_address]),
                json={'ports': [{'address': mac_address,
                                 'node_uuid': port_node_uuid,
                                 'uuid': port_uuid}]}),
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='ports',
                    append=[self.fake_baremetal_port['uuid']])),
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']])),
        ])

        self.cloud.unregister_machine(
            nics, self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_unregister_machine_locked_timeout(self):
        mac_address = self.fake_baremetal_port['address']
        nics = [{'mac': mac_address}]
        self.fake_baremetal_node['provision_state'] = 'available'
        self.fake_baremetal_node['reservation'] = 'conductor99'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.unregister_machine,
            nics,
            self.fake_baremetal_node['uuid'],
            timeout=0.001)
        self.assert_calls()

    def test_unregister_machine_retries(self):
        mac_address = self.fake_baremetal_port['address']
        nics = [{'mac': mac_address}]
        port_uuid = self.fake_baremetal_port['uuid']
        # NOTE(TheJulia): The two values below should be the same.
        port_node_uuid = self.fake_baremetal_port['node_uuid']
        self.fake_baremetal_node['provision_state'] = 'available'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='ports',
                    qs_elements=['address=%s' % mac_address]),
                json={'ports': [{'address': mac_address,
                                 'node_uuid': port_node_uuid,
                                 'uuid': port_uuid}]}),
            dict(
                method='DELETE',
                status_code=503,
                uri=self.get_mock_url(
                    resource='ports',
                    append=[self.fake_baremetal_port['uuid']])),
            dict(
                method='DELETE',
                status_code=409,
                uri=self.get_mock_url(
                    resource='ports',
                    append=[self.fake_baremetal_port['uuid']])),
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='ports',
                    append=[self.fake_baremetal_port['uuid']])),
            dict(
                method='DELETE',
                status_code=409,
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']])),
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']])),
        ])

        self.cloud.unregister_machine(
            nics, self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_unregister_machine_unavailable(self):
        # This is a list of invalid states that the method
        # should fail on.
        invalid_states = ['active', 'cleaning', 'clean wait', 'clean failed']
        mac_address = self.fake_baremetal_port['address']
        nics = [{'mac': mac_address}]
        url_list = []
        for state in invalid_states:
            self.fake_baremetal_node['provision_state'] = state
            url_list.append(
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        resource='nodes',
                        append=[self.fake_baremetal_node['uuid']]),
                    json=self.fake_baremetal_node))

        self.register_uris(url_list)

        for state in invalid_states:
            self.assertRaises(
                exc.OpenStackCloudException,
                self.cloud.unregister_machine,
                nics,
                self.fake_baremetal_node['uuid'])

        self.assert_calls()

    def test_update_machine_patch_no_action(self):
        self.register_uris([dict(
            method='GET',
            uri=self.get_mock_url(
                resource='nodes',
                append=[self.fake_baremetal_node['uuid']]),
            json=self.fake_baremetal_node),
        ])
        # NOTE(TheJulia): This is just testing mechanics.
        update_dict = self.cloud.update_machine(
            self.fake_baremetal_node['uuid'])
        self.assertIsNone(update_dict['changes'])
        self.assertSubdict(self.fake_baremetal_node, update_dict['node'])

        self.assert_calls()

    def test_attach_port_to_machine(self):
        vif_id = '953ccbee-e854-450f-95fe-fe5e40d611ec'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    service_type='network',
                    resource='ports.json',
                    base_url_append='v2.0'),
                json={'ports': [{'id': vif_id}]}),
            dict(
                method='POST',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'], 'vifs'])),
        ])
        self.cloud.attach_port_to_machine(self.fake_baremetal_node['uuid'],
                                          vif_id)
        self.assert_calls()

    def test_detach_port_from_machine(self):
        vif_id = '953ccbee-e854-450f-95fe-fe5e40d611ec'
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    service_type='network',
                    resource='ports.json',
                    base_url_append='v2.0'),
                json={'ports': [{'id': vif_id}]}),
            dict(
                method='DELETE',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'], 'vifs',
                            vif_id])),
        ])
        self.cloud.detach_port_from_machine(self.fake_baremetal_node['uuid'],
                                            vif_id)
        self.assert_calls()

    def test_list_ports_attached_to_machine(self):
        vif_id = '953ccbee-e854-450f-95fe-fe5e40d611ec'
        fake_port = {'id': vif_id, 'name': 'test'}
        self.register_uris([
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid']]),
                json=self.fake_baremetal_node),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    resource='nodes',
                    append=[self.fake_baremetal_node['uuid'], 'vifs']),
                json={'vifs': [{'id': vif_id}]}),
            dict(
                method='GET',
                uri=self.get_mock_url(
                    service_type='network',
                    resource='ports.json',
                    base_url_append='v2.0'),
                json={'ports': [fake_port]}),
        ])
        res = self.cloud.list_ports_attached_to_machine(
            self.fake_baremetal_node['uuid'])
        self.assert_calls()
        self.assertEqual([fake_port], res)


class TestUpdateMachinePatch(base.IronicTestCase):
    # NOTE(TheJulia): As appears, and mordred describes,
    # this class utilizes black magic, which ultimately
    # results in additional test runs being executed with
    # the scenario name appended. Useful for lots of
    # variables that need to be tested.

    def setUp(self):
        super(TestUpdateMachinePatch, self).setUp()
        self.fake_baremetal_node = fakes.make_fake_machine(
            self.name, self.uuid)

    def test_update_machine_patch(self):
        # The model has evolved over time, create the field if
        # we don't already have it.
        if self.field_name not in self.fake_baremetal_node:
            self.fake_baremetal_node[self.field_name] = None
        value_to_send = self.fake_baremetal_node[self.field_name]
        if self.changed:
            value_to_send = self.new_value
        uris = [dict(
            method='GET',
            uri=self.get_mock_url(
                resource='nodes',
                append=[self.fake_baremetal_node['uuid']]),
            json=self.fake_baremetal_node),
        ]
        if self.changed:
            test_patch = [{
                'op': 'replace',
                'path': '/' + self.field_name,
                'value': value_to_send}]
            uris.append(
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(
                        resource='nodes',
                        append=[self.fake_baremetal_node['uuid']]),
                    json=self.fake_baremetal_node,
                    validate=dict(json=test_patch)))

        self.register_uris(uris)

        call_args = {self.field_name: value_to_send}
        update_dict = self.cloud.update_machine(
            self.fake_baremetal_node['uuid'], **call_args)

        if self.changed:
            self.assertEqual(['/' + self.field_name], update_dict['changes'])
        else:
            self.assertIsNone(update_dict['changes'])
        self.assertSubdict(self.fake_baremetal_node, update_dict['node'])

        self.assert_calls()

    scenarios = [
        ('chassis_uuid', dict(field_name='chassis_uuid', changed=False)),
        ('chassis_uuid_changed',
         dict(field_name='chassis_uuid', changed=True,
              new_value='meow')),
        ('driver', dict(field_name='driver', changed=False)),
        ('driver_changed', dict(field_name='driver', changed=True,
                                new_value='meow')),
        ('driver_info', dict(field_name='driver_info', changed=False)),
        ('driver_info_changed', dict(field_name='driver_info', changed=True,
                                     new_value={'cat': 'meow'})),
        ('instance_info', dict(field_name='instance_info', changed=False)),
        ('instance_info_changed',
         dict(field_name='instance_info', changed=True,
              new_value={'cat': 'meow'})),
        ('instance_uuid', dict(field_name='instance_uuid', changed=False)),
        ('instance_uuid_changed',
         dict(field_name='instance_uuid', changed=True,
              new_value='meow')),
        ('name', dict(field_name='name', changed=False)),
        ('name_changed', dict(field_name='name', changed=True,
                              new_value='meow')),
        ('properties', dict(field_name='properties', changed=False)),
        ('properties_changed', dict(field_name='properties', changed=True,
                                    new_value={'cat': 'meow'}))
    ]
