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

from shade import exc
from shade.tests import fakes
from shade.tests.unit import base


class TestBaremetalNode(base.IronicTestCase):

    def setUp(self):
        super(TestBaremetalNode, self).setUp()
        self.fake_baremetal_node = fakes.make_fake_machine(
            self.name, self.uuid)

    def test_list_machines(self):
        fake_baremetal_two = fakes.make_fake_machine('two', str(uuid.uuid4()))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='nodes'),
                 json={'nodes': [self.fake_baremetal_node,
                                 fake_baremetal_two]}),
        ])

        machines = self.op_cloud.list_machines()
        self.assertEqual(2, len(machines))
        self.assertEqual(self.fake_baremetal_node, machines[0])
        self.assert_calls()

    def test_get_machine(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        machine = self.op_cloud.get_machine(self.fake_baremetal_node['uuid'])
        self.assertEqual(machine['uuid'],
                         self.fake_baremetal_node['uuid'])
        self.assert_calls()

    def test_get_machine_by_mac(self):
        mac_address = '00:01:02:03:04:05'
        url_address = 'detail?address=%s' % mac_address
        node_uuid = self.fake_baremetal_node['uuid']
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='ports',
                     append=[url_address]),
                 json={'ports': [{'address': mac_address,
                                  'node_uuid': node_uuid}]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        machine = self.op_cloud.get_machine_by_mac(mac_address)
        self.assertEqual(machine['uuid'],
                         self.fake_baremetal_node['uuid'])
        self.assert_calls()

    def test_validate_node(self):
        # NOTE(TheJulia): Note: These are only the interfaces
        # that are validated, and both must be true for an
        # exception to not be raised.
        # This should be fixed at some point, as some interfaces
        # are important in some cases and should be validated,
        # such as storage.
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
        self.op_cloud.validate_node(self.fake_baremetal_node['uuid'])

        self.assert_calls()

    # FIXME(TheJulia): So, this doesn't presently fail, but should fail.
    # Placing the test here, so we can sort out the issue in the actual
    # method later.
    # def test_validate_node_raises_exception(self):
    #    validate_return = {
    #        'deploy': {
    #            'result': False,
    #            'reason': 'error!',
    #        },
    #        'power': {
    #            'result': False,
    #            'reason': 'meow!',
    #        },
    #        'foo': {
    #            'result': True
    #        }}
    #    self.register_uris([
    #        dict(method='GET',
    #             uri=self.get_mock_url(
    #                 resource='nodes',
    #                 append=[self.fake_baremetal_node['uuid'],
    #                         'validate']),
    #             json=validate_return),
    #    ])
    #    self.assertRaises(
    #        Exception,
    #        self.op_cloud.validate_node,
    #        self.fake_baremetal_node['uuid'])
    #
    #    self.assert_calls()

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
        self.op_cloud.patch_machine(self.fake_baremetal_node['uuid'],
                                    test_patch)

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
        self.op_cloud.set_node_instance_info(
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
        self.op_cloud.purge_node_instance_info(
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
            self.op_cloud.inspect_machine,
            self.fake_baremetal_node['uuid'],
            wait=True,
            timeout=1)

        self.assert_calls()

    def test_inspect_machine_failed(self):
        inspecting_node = self.fake_baremetal_node.copy()
        self.fake_baremetal_node['provision_state'] = 'inspect failed'
        self.fake_baremetal_node['last_error'] = 'kaboom!'
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
                json=inspecting_node)
        ])

        self.op_cloud.inspect_machine(self.fake_baremetal_node['uuid'])

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
        ])
        self.op_cloud.inspect_machine(self.fake_baremetal_node['uuid'])

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
        self.op_cloud.inspect_machine(self.fake_baremetal_node['uuid'])

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
        self.op_cloud.inspect_machine(self.fake_baremetal_node['uuid'],
                                      wait=True, timeout=1)

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
        self.op_cloud.inspect_machine(self.fake_baremetal_node['uuid'],
                                      wait=True, timeout=1)

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
                          self.op_cloud.inspect_machine,
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
        ])
        self.op_cloud.set_machine_maintenance_state(
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
        ])
        self.op_cloud.set_machine_maintenance_state(
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
        ])
        self.op_cloud.remove_machine_from_maintenance(
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
        return_value = self.op_cloud.set_machine_power_on(
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
        return_value = self.op_cloud.set_machine_power_off(
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
        return_value = self.op_cloud.set_machine_power_reboot(
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
                          self.op_cloud.set_machine_power_reboot,
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
        self.op_cloud.node_set_provision_state(
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
        return_value = self.op_cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'active',
            wait=True)

        self.assertEqual(active_node, return_value)
        self.assert_calls()

    def test_node_set_provision_state_wait_timeout_fails(self):
        # Intentionally time out.
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
            self.op_cloud.node_set_provision_state,
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

        return_value = self.op_cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'active',
            wait=True)

        self.assertEqual(self.fake_baremetal_node, return_value)
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
            self.op_cloud.node_set_provision_state,
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
        return_value = self.op_cloud.node_set_provision_state(
            self.fake_baremetal_node['uuid'],
            'provide',
            wait=True)

        self.assertEqual(available_node, return_value)
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
        return_value = self.op_cloud.activate_node(
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
        return_value = self.op_cloud.deactivate_node(
            self.fake_baremetal_node['uuid'],
            wait=True)

        self.assertIsNone(return_value)
        self.assert_calls()

    def _test_update_machine(self, fake_node, field_name, changed=True):
        # The model has evolved over time, create the field if
        # we don't already have it.
        if field_name not in fake_node:
            fake_node[field_name] = None
        value_to_send = fake_node[field_name]
        if changed:
            value_to_send = 'meow'
        uris = [dict(
            method='GET',
            uri=self.get_mock_url(
                resource='nodes',
                append=[fake_node['uuid']]),
            json=fake_node),
        ]
        if changed:
            test_patch = [{
                'op': 'replace',
                'path': '/' + field_name,
                'value': 'meow'}]
            uris.append(
                dict(
                    method='PATCH',
                    uri=self.get_mock_url(
                        resource='nodes',
                        append=[fake_node['uuid']]),
                    json=fake_node,
                    validate=dict(json=test_patch)))

        self.register_uris(uris)

        call_args = {field_name: value_to_send}
        update_dict = self.op_cloud.update_machine(
            fake_node['uuid'], **call_args)

        if not changed:
            self.assertIsNone(update_dict['changes'])
        self.assertDictEqual(fake_node, update_dict['node'])

        self.assert_calls()

    def test_update_machine_patch_name(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'name', False)

    def test_update_machine_patch_chassis_uuid(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'chassis_uuid', False)

    def test_update_machine_patch_driver(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'driver', False)

    def test_update_machine_patch_driver_info(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'driver_info', False)

    def test_update_machine_patch_instance_info(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'instance_info', False)

    def test_update_machine_patch_instance_uuid(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'instance_uuid', False)

    def test_update_machine_patch_properties(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'properties', False)

    def test_update_machine_patch_update_name(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'name', True)

    def test_update_machine_patch_update_chassis_uuid(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'chassis_uuid', True)

    def test_update_machine_patch_update_driver(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'driver', True)

    def test_update_machine_patch_update_driver_info(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'driver_info', True)

    def test_update_machine_patch_update_instance_info(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'instance_info', True)

    def test_update_machine_patch_update_instance_uuid(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'instance_uuid', True)

    def test_update_machine_patch_update_properties(self):
        self._test_update_machine(self.fake_baremetal_node,
                                  'properties', True)

    def test_update_machine_patch_no_action(self):
        self.register_uris([dict(
            method='GET',
            uri=self.get_mock_url(
                resource='nodes',
                append=[self.fake_baremetal_node['uuid']]),
            json=self.fake_baremetal_node),
        ])
        # NOTE(TheJulia): This is just testing mechanics.
        update_dict = self.op_cloud.update_machine(
            self.fake_baremetal_node['uuid'])
        self.assertIsNone(update_dict['changes'])
        self.assertDictEqual(self.fake_baremetal_node, update_dict['node'])

        self.assert_calls()
