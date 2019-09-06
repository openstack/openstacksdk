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

import uuid

from openstack import exceptions
from openstack.tests.functional.baremetal import base


class TestBareMetalNode(base.BaseBaremetalTest):
    def test_node_create_get_delete(self):
        node = self.create_node(name='node-name')
        self.assertEqual(node.name, 'node-name')
        self.assertEqual(node.driver, 'fake-hardware')
        self.assertEqual(node.provision_state, 'available')
        self.assertFalse(node.is_maintenance)

        # NOTE(dtantsur): get_node and find_node only differ in handing missing
        # nodes, otherwise they are identical.
        for call, ident in [(self.conn.baremetal.get_node, self.node_id),
                            (self.conn.baremetal.get_node, 'node-name'),
                            (self.conn.baremetal.find_node, self.node_id),
                            (self.conn.baremetal.find_node, 'node-name')]:
            found = call(ident)
            self.assertEqual(node.id, found.id)
            self.assertEqual(node.name, found.name)

        with_fields = self.conn.baremetal.get_node(
            'node-name',
            fields=['uuid', 'driver', 'instance_id'])
        self.assertEqual(node.id, with_fields.id)
        self.assertEqual(node.driver, with_fields.driver)
        self.assertIsNone(with_fields.name)
        self.assertIsNone(with_fields.provision_state)

        nodes = self.conn.baremetal.nodes()
        self.assertIn(node.id, [n.id for n in nodes])

        self.conn.baremetal.delete_node(node, ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_node, self.node_id)

    def test_node_update(self):
        node = self.create_node(name='node-name', extra={'foo': 'bar'})
        node.name = 'new-name'
        node.extra = {'answer': 42}
        instance_uuid = str(uuid.uuid4())

        node = self.conn.baremetal.update_node(node,
                                               instance_id=instance_uuid)
        self.assertEqual('new-name', node.name)
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.conn.baremetal.get_node('new-name')
        self.assertEqual('new-name', node.name)
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.conn.baremetal.update_node(node,
                                               instance_id=None)
        self.assertIsNone(node.instance_id)

        node = self.conn.baremetal.get_node('new-name')
        self.assertIsNone(node.instance_id)

    def test_node_update_by_name(self):
        self.create_node(name='node-name', extra={'foo': 'bar'})
        instance_uuid = str(uuid.uuid4())

        node = self.conn.baremetal.update_node('node-name',
                                               instance_id=instance_uuid,
                                               extra={'answer': 42})
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.conn.baremetal.get_node('node-name')
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.conn.baremetal.update_node('node-name',
                                               instance_id=None)
        self.assertIsNone(node.instance_id)

        node = self.conn.baremetal.get_node('node-name')
        self.assertIsNone(node.instance_id)

    def test_node_patch(self):
        node = self.create_node(name='node-name', extra={'foo': 'bar'})
        node.name = 'new-name'
        instance_uuid = str(uuid.uuid4())

        node = self.conn.baremetal.patch_node(
            node,
            [dict(path='/instance_id', op='replace', value=instance_uuid),
             dict(path='/extra/answer', op='add', value=42)])
        self.assertEqual('new-name', node.name)
        self.assertEqual({'foo': 'bar', 'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.conn.baremetal.get_node('new-name')
        self.assertEqual('new-name', node.name)
        self.assertEqual({'foo': 'bar', 'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.conn.baremetal.patch_node(
            node,
            [dict(path='/instance_id', op='remove'),
             dict(path='/extra/answer', op='remove')])
        self.assertIsNone(node.instance_id)
        self.assertNotIn('answer', node.extra)

        node = self.conn.baremetal.get_node('new-name')
        self.assertIsNone(node.instance_id)
        self.assertNotIn('answer', node.extra)

    def test_node_list_update_delete(self):
        self.create_node(name='node-name', extra={'foo': 'bar'})
        node = next(n for n in
                    self.conn.baremetal.nodes(details=True,
                                              provision_state='available',
                                              is_maintenance=False,
                                              associated=False)
                    if n.name == 'node-name')
        self.assertEqual(node.extra, {'foo': 'bar'})

        # This test checks that resources returned from listing are usable
        self.conn.baremetal.update_node(node, extra={'foo': 42})
        self.conn.baremetal.delete_node(node, ignore_missing=False)

    def test_node_create_in_enroll_provide(self):
        node = self.create_node(provision_state='enroll')
        self.node_id = node.id

        self.assertEqual(node.driver, 'fake-hardware')
        self.assertEqual(node.provision_state, 'enroll')
        self.assertIsNone(node.power_state)
        self.assertFalse(node.is_maintenance)

        self.conn.baremetal.set_node_provision_state(node, 'manage',
                                                     wait=True)
        self.assertEqual(node.provision_state, 'manageable')

        self.conn.baremetal.set_node_provision_state(node, 'provide',
                                                     wait=True)
        self.assertEqual(node.provision_state, 'available')

    def test_node_power_state(self):
        node = self.create_node()
        self.assertIsNone(node.power_state)

        self.conn.baremetal.set_node_power_state(node, 'power on')
        node = self.conn.baremetal.get_node(node.id)
        # Fake nodes react immediately to power requests.
        self.assertEqual('power on', node.power_state)

        self.conn.baremetal.set_node_power_state(node, 'power off')
        node = self.conn.baremetal.get_node(node.id)
        self.assertEqual('power off', node.power_state)

    def test_node_validate(self):
        node = self.create_node()
        # Fake hardware passes validation for all interfaces
        result = self.conn.baremetal.validate_node(node)
        for iface in ('boot', 'deploy', 'management', 'power'):
            self.assertTrue(result[iface].result)
            self.assertFalse(result[iface].reason)

    def test_node_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_node, uuid)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.find_node, uuid,
                          ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.delete_node, uuid,
                          ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.update_node, uuid,
                          name='new-name')
        self.assertIsNone(self.conn.baremetal.find_node(uuid))
        self.assertIsNone(self.conn.baremetal.delete_node(uuid))

    def test_maintenance(self):
        reason = "Prepating for taking over the world"

        node = self.create_node()
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Initial setting without the reason
        node = self.conn.baremetal.set_node_maintenance(node)
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Updating the reason later
        node = self.conn.baremetal.set_node_maintenance(node, reason)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Removing the reason later
        node = self.conn.baremetal.set_node_maintenance(node)
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Unsetting maintenance
        node = self.conn.baremetal.unset_node_maintenance(node)
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Initial setting with the reason
        node = self.conn.baremetal.set_node_maintenance(node, reason)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

    def test_maintenance_via_update(self):
        reason = "Prepating for taking over the world"

        node = self.create_node()

        # Initial setting without the reason
        node = self.conn.baremetal.update_node(node, is_maintenance=True)
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.conn.baremetal.get_node(node.id)
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Updating the reason later
        node = self.conn.baremetal.update_node(node, maintenance_reason=reason)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.conn.baremetal.get_node(node.id)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Unsetting maintenance
        node = self.conn.baremetal.update_node(node, is_maintenance=False)
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.conn.baremetal.get_node(node.id)
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Initial setting with the reason
        node = self.conn.baremetal.update_node(node, is_maintenance=True,
                                               maintenance_reason=reason)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.conn.baremetal.get_node(node.id)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)


class TestBareMetalNodeFields(base.BaseBaremetalTest):

    min_microversion = '1.8'

    def test_node_fields(self):
        self.create_node()
        result = self.conn.baremetal.nodes(
            fields=['uuid', 'name', 'instance_id'])
        for item in result:
            self.assertIsNotNone(item.id)
            self.assertIsNone(item.driver)


class TestBareMetalVif(base.BaseBaremetalTest):

    min_microversion = '1.28'

    def setUp(self):
        super(TestBareMetalVif, self).setUp()
        self.node = self.create_node(network_interface='noop')
        self.vif_id = "200712fc-fdfb-47da-89a6-2d19f76c7618"

    def test_node_vif_attach_detach(self):
        self.conn.baremetal.attach_vif_to_node(self.node, self.vif_id)
        # NOTE(dtantsur): The noop networking driver is completely noop - the
        # VIF list does not return anything of value.
        self.conn.baremetal.list_node_vifs(self.node)
        res = self.conn.baremetal.detach_vif_from_node(self.node, self.vif_id,
                                                       ignore_missing=False)
        self.assertTrue(res)

    def test_node_vif_negative(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.attach_vif_to_node,
                          uuid, self.vif_id)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.list_node_vifs,
                          uuid)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.detach_vif_from_node,
                          uuid, self.vif_id, ignore_missing=False)


class TestTraits(base.BaseBaremetalTest):

    min_microversion = '1.37'

    def setUp(self):
        super(TestTraits, self).setUp()
        self.node = self.create_node()

    def test_add_remove_node_trait(self):
        node = self.conn.baremetal.get_node(self.node)
        self.assertEqual([], node.traits)

        self.conn.baremetal.add_node_trait(self.node, 'CUSTOM_FAKE')
        self.assertEqual(['CUSTOM_FAKE'], self.node.traits)
        node = self.conn.baremetal.get_node(self.node)
        self.assertEqual(['CUSTOM_FAKE'], node.traits)

        self.conn.baremetal.add_node_trait(self.node, 'CUSTOM_REAL')
        self.assertEqual(sorted(['CUSTOM_FAKE', 'CUSTOM_REAL']),
                         sorted(self.node.traits))
        node = self.conn.baremetal.get_node(self.node)
        self.assertEqual(sorted(['CUSTOM_FAKE', 'CUSTOM_REAL']),
                         sorted(node.traits))

        self.conn.baremetal.remove_node_trait(node, 'CUSTOM_FAKE',
                                              ignore_missing=False)
        self.assertEqual(['CUSTOM_REAL'], self.node.traits)
        node = self.conn.baremetal.get_node(self.node)
        self.assertEqual(['CUSTOM_REAL'], node.traits)

    def test_set_node_traits(self):
        node = self.conn.baremetal.get_node(self.node)
        self.assertEqual([], node.traits)

        traits1 = ['CUSTOM_FAKE', 'CUSTOM_REAL']
        traits2 = ['CUSTOM_FOOBAR']

        self.conn.baremetal.set_node_traits(self.node, traits1)
        self.assertEqual(sorted(traits1), sorted(self.node.traits))
        node = self.conn.baremetal.get_node(self.node)
        self.assertEqual(sorted(traits1), sorted(node.traits))

        self.conn.baremetal.set_node_traits(self.node, traits2)
        self.assertEqual(['CUSTOM_FOOBAR'], self.node.traits)
        node = self.conn.baremetal.get_node(self.node)
        self.assertEqual(['CUSTOM_FOOBAR'], node.traits)
