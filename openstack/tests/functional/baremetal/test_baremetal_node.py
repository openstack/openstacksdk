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

import random
import uuid

from openstack import exceptions
from openstack.tests.functional.baremetal import base


class TestBareMetalNode(base.BaseBaremetalTest):
    def test_node_create_get_delete(self):
        node = self.create_node(name='node-name')
        self.assertEqual(node.name, 'node-name')
        self.assertEqual(node.driver, 'fake-hardware')
        self.assertEqual(node.provision_state, 'enroll')
        self.assertFalse(node.is_maintenance)

        # NOTE(dtantsur): get_node and find_node only differ in handing missing
        # nodes, otherwise they are identical.
        for call, ident in [
            (self.operator_cloud.baremetal.get_node, self.node_id),
            (self.operator_cloud.baremetal.get_node, 'node-name'),
            (self.operator_cloud.baremetal.find_node, self.node_id),
            (self.operator_cloud.baremetal.find_node, 'node-name'),
        ]:
            found = call(ident)
            self.assertEqual(node.id, found.id)
            self.assertEqual(node.name, found.name)

        with_fields = self.operator_cloud.baremetal.get_node(
            'node-name', fields=['uuid', 'driver', 'instance_id']
        )
        self.assertEqual(node.id, with_fields.id)
        self.assertEqual(node.driver, with_fields.driver)
        self.assertIsNone(with_fields.name)
        self.assertIsNone(with_fields.provision_state)

        nodes = self.operator_cloud.baremetal.nodes()
        self.assertIn(node.id, [n.id for n in nodes])

        self.operator_cloud.baremetal.delete_node(node, ignore_missing=False)
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_node,
            self.node_id,
        )

    def test_node_create_in_available(self):
        node = self.create_node(name='node-name', provision_state='available')
        self.assertEqual(node.name, 'node-name')
        self.assertEqual(node.driver, 'fake-hardware')
        self.assertEqual(node.provision_state, 'available')

        self.operator_cloud.baremetal.delete_node(node, ignore_missing=False)
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_node,
            self.node_id,
        )

    def test_node_update(self):
        node = self.create_node(name='node-name', extra={'foo': 'bar'})
        node.name = 'new-name'
        node.extra = {'answer': 42}
        instance_uuid = str(uuid.uuid4())

        node = self.operator_cloud.baremetal.update_node(
            node, instance_id=instance_uuid
        )
        self.assertEqual('new-name', node.name)
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.operator_cloud.baremetal.get_node('new-name')
        self.assertEqual('new-name', node.name)
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.operator_cloud.baremetal.update_node(
            node, instance_id=None
        )
        self.assertIsNone(node.instance_id)

        node = self.operator_cloud.baremetal.get_node('new-name')
        self.assertIsNone(node.instance_id)

    def test_node_update_by_name(self):
        self.create_node(name='node-name', extra={'foo': 'bar'})
        instance_uuid = str(uuid.uuid4())

        node = self.operator_cloud.baremetal.update_node(
            'node-name', instance_id=instance_uuid, extra={'answer': 42}
        )
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.operator_cloud.baremetal.get_node('node-name')
        self.assertEqual({'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.operator_cloud.baremetal.update_node(
            'node-name', instance_id=None
        )
        self.assertIsNone(node.instance_id)

        node = self.operator_cloud.baremetal.get_node('node-name')
        self.assertIsNone(node.instance_id)

    def test_node_patch(self):
        node = self.create_node(name='node-name', extra={'foo': 'bar'})
        node.name = 'new-name'
        instance_uuid = str(uuid.uuid4())

        node = self.operator_cloud.baremetal.patch_node(
            node,
            [
                dict(path='/instance_id', op='replace', value=instance_uuid),
                dict(path='/extra/answer', op='add', value=42),
            ],
        )
        self.assertEqual('new-name', node.name)
        self.assertEqual({'foo': 'bar', 'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.operator_cloud.baremetal.get_node('new-name')
        self.assertEqual('new-name', node.name)
        self.assertEqual({'foo': 'bar', 'answer': 42}, node.extra)
        self.assertEqual(instance_uuid, node.instance_id)

        node = self.operator_cloud.baremetal.patch_node(
            node,
            [
                dict(path='/instance_id', op='remove'),
                dict(path='/extra/answer', op='remove'),
            ],
        )
        self.assertIsNone(node.instance_id)
        self.assertNotIn('answer', node.extra)

        node = self.operator_cloud.baremetal.get_node('new-name')
        self.assertIsNone(node.instance_id)
        self.assertNotIn('answer', node.extra)

    def test_node_list_update_delete(self):
        self.create_node(name='node-name', extra={'foo': 'bar'})
        node = next(
            n
            for n in self.operator_cloud.baremetal.nodes(
                details=True,
                provision_state='enroll',
                is_maintenance=False,
                associated=False,
            )
            if n.name == 'node-name'
        )
        self.assertEqual(node.extra, {'foo': 'bar'})

        # This test checks that resources returned from listing are usable
        self.operator_cloud.baremetal.update_node(node, extra={'foo': 42})
        self.operator_cloud.baremetal.delete_node(node, ignore_missing=False)

    def test_node_create_in_enroll_provide(self):
        node = self.create_node()
        self.node_id = node.id

        self.assertEqual(node.driver, 'fake-hardware')
        self.assertEqual(node.provision_state, 'enroll')
        self.assertIsNone(node.power_state)
        self.assertFalse(node.is_maintenance)

        self.operator_cloud.baremetal.set_node_provision_state(
            node, 'manage', wait=True
        )
        self.assertEqual(node.provision_state, 'manageable')

        self.operator_cloud.baremetal.set_node_provision_state(
            node, 'provide', wait=True
        )
        self.assertEqual(node.provision_state, 'available')

    def test_node_create_in_enroll_provide_by_name(self):
        name = f'node-{random.randint(0, 1000)}'
        node = self.create_node(name=name)
        self.node_id = node.id

        self.assertEqual(node.driver, 'fake-hardware')
        self.assertEqual(node.provision_state, 'enroll')
        self.assertIsNone(node.power_state)
        self.assertFalse(node.is_maintenance)

        node = self.operator_cloud.baremetal.set_node_provision_state(
            name, 'manage', wait=True
        )
        self.assertEqual(node.provision_state, 'manageable')

        node = self.operator_cloud.baremetal.set_node_provision_state(
            name, 'provide', wait=True
        )
        self.assertEqual(node.provision_state, 'available')

    def test_node_power_state(self):
        node = self.create_node()
        self.assertIsNone(node.power_state)

        self.operator_cloud.baremetal.set_node_power_state(
            node, 'power on', wait=True
        )
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertEqual('power on', node.power_state)

        self.operator_cloud.baremetal.set_node_power_state(
            node, 'power off', wait=True
        )
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertEqual('power off', node.power_state)

    def test_node_validate(self):
        node = self.create_node()
        # Fake hardware passes validation for all interfaces
        result = self.operator_cloud.baremetal.validate_node(node)
        for iface in ('boot', 'deploy', 'management', 'power'):
            self.assertTrue(result[iface].result)
            self.assertFalse(result[iface].reason)

    def test_node_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_node,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.find_node,
            uuid,
            ignore_missing=False,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.delete_node,
            uuid,
            ignore_missing=False,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.update_node,
            uuid,
            name='new-name',
        )
        self.assertIsNone(self.operator_cloud.baremetal.find_node(uuid))
        self.assertIsNone(self.operator_cloud.baremetal.delete_node(uuid))

    def test_maintenance(self):
        reason = "Prepating for taking over the world"

        node = self.create_node()
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Initial setting without the reason
        node = self.operator_cloud.baremetal.set_node_maintenance(node)
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Updating the reason later
        node = self.operator_cloud.baremetal.set_node_maintenance(node, reason)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Removing the reason later
        node = self.operator_cloud.baremetal.set_node_maintenance(node)
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Unsetting maintenance
        node = self.operator_cloud.baremetal.unset_node_maintenance(node)
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Initial setting with the reason
        node = self.operator_cloud.baremetal.set_node_maintenance(node, reason)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

    def test_maintenance_via_update(self):
        reason = "Prepating for taking over the world"

        node = self.create_node()

        # Initial setting without the reason
        node = self.operator_cloud.baremetal.update_node(
            node, is_maintenance=True
        )
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertTrue(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Updating the reason later
        node = self.operator_cloud.baremetal.update_node(
            node, maintenance_reason=reason
        )
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Unsetting maintenance
        node = self.operator_cloud.baremetal.update_node(
            node, is_maintenance=False
        )
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertFalse(node.is_maintenance)
        self.assertIsNone(node.maintenance_reason)

        # Initial setting with the reason
        node = self.operator_cloud.baremetal.update_node(
            node, is_maintenance=True, maintenance_reason=reason
        )
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)

        # Make sure the change has effect on the remote side.
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertTrue(node.is_maintenance)
        self.assertEqual(reason, node.maintenance_reason)


class TestNodeRetired(base.BaseBaremetalTest):
    min_microversion = '1.61'

    def test_retired(self):
        reason = "I'm too old for this s...tuff!"

        node = self.create_node()

        # Set retired without reason
        node = self.operator_cloud.baremetal.update_node(node, is_retired=True)
        self.assertTrue(node.is_retired)
        self.assertIsNone(node.retired_reason)

        # Verify set retired on server side
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertTrue(node.is_retired)
        self.assertIsNone(node.retired_reason)

        # Add the reason
        node = self.operator_cloud.baremetal.update_node(
            node, retired_reason=reason
        )
        self.assertTrue(node.is_retired)
        self.assertEqual(reason, node.retired_reason)

        # Verify the reason on server side
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertTrue(node.is_retired)
        self.assertEqual(reason, node.retired_reason)

        # Unset retired
        node = self.operator_cloud.baremetal.update_node(
            node, is_retired=False
        )
        self.assertFalse(node.is_retired)
        self.assertIsNone(node.retired_reason)

        # Verify on server side
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertFalse(node.is_retired)
        self.assertIsNone(node.retired_reason)

        # Set retired with reason
        node = self.operator_cloud.baremetal.update_node(
            node, is_retired=True, retired_reason=reason
        )
        self.assertTrue(node.is_retired)
        self.assertEqual(reason, node.retired_reason)

        # Verify on server side
        node = self.operator_cloud.baremetal.get_node(node.id)
        self.assertTrue(node.is_retired)
        self.assertEqual(reason, node.retired_reason)

    def test_retired_in_available(self):
        node = self.create_node(provision_state='available')

        # Set retired when node state available should fail!
        self.assertRaises(
            exceptions.ConflictException,
            self.operator_cloud.baremetal.update_node,
            node,
            is_retired=True,
        )


class TestBareMetalNodeFields(base.BaseBaremetalTest):
    min_microversion = '1.8'

    def test_node_fields(self):
        self.create_node()
        result = self.operator_cloud.baremetal.nodes(
            fields=['uuid', 'name', 'instance_id']
        )
        for item in result:
            self.assertIsNotNone(item.id)
            self.assertIsNone(item.driver)


class TestBareMetalVif(base.BaseBaremetalTest):
    min_microversion = '1.28'

    def setUp(self):
        super().setUp()
        self.node = self.create_node(network_interface='noop')
        self.vif_id = "200712fc-fdfb-47da-89a6-2d19f76c7618"

    def test_node_vif_attach_detach(self):
        self.operator_cloud.baremetal.attach_vif_to_node(
            self.node, self.vif_id
        )
        # NOTE(dtantsur): The noop networking driver is completely noop - the
        # VIF list does not return anything of value.
        self.operator_cloud.baremetal.list_node_vifs(self.node)
        res = self.operator_cloud.baremetal.detach_vif_from_node(
            self.node, self.vif_id, ignore_missing=False
        )
        self.assertTrue(res)

    def test_node_vif_negative(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.attach_vif_to_node,
            uuid,
            self.vif_id,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.list_node_vifs,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.detach_vif_from_node,
            uuid,
            self.vif_id,
            ignore_missing=False,
        )


class TestBareMetalVirtualMedia(base.BaseBaremetalTest):
    min_microversion = '1.89'

    def setUp(self):
        super().setUp()
        self.node = self.create_node(network_interface='noop')
        self.device_type = "CDROM"
        self.image_url = "http://image"

    def test_node_vmedia_attach_detach(self):
        self.conn.baremetal.attach_vmedia_to_node(
            self.node, self.device_type, self.image_url
        )
        res = self.conn.baremetal.detach_vmedia_from_node(self.node)
        self.assertNone(res)

    def test_node_vmedia_negative(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(
            exceptions.ResourceNotFound,
            self.conn.baremetal.attach_vmedia_to_node,
            uuid,
            self.device_type,
            self.image_url,
        )
        self.assertRaises(
            exceptions.ResourceNotFound,
            self.conn.baremetal.detach_vmedia_from_node,
            uuid,
        )


class TestTraits(base.BaseBaremetalTest):
    min_microversion = '1.37'

    def setUp(self):
        super().setUp()
        self.node = self.create_node()

    def test_add_remove_node_trait(self):
        node = self.operator_cloud.baremetal.get_node(self.node)
        self.assertEqual([], node.traits)

        self.operator_cloud.baremetal.add_node_trait(self.node, 'CUSTOM_FAKE')
        self.assertEqual(['CUSTOM_FAKE'], self.node.traits)
        node = self.operator_cloud.baremetal.get_node(self.node)
        self.assertEqual(['CUSTOM_FAKE'], node.traits)

        self.operator_cloud.baremetal.add_node_trait(self.node, 'CUSTOM_REAL')
        self.assertEqual(
            sorted(['CUSTOM_FAKE', 'CUSTOM_REAL']), sorted(self.node.traits)
        )
        node = self.operator_cloud.baremetal.get_node(self.node)
        self.assertEqual(
            sorted(['CUSTOM_FAKE', 'CUSTOM_REAL']), sorted(node.traits)
        )

        self.operator_cloud.baremetal.remove_node_trait(
            node, 'CUSTOM_FAKE', ignore_missing=False
        )
        self.assertEqual(['CUSTOM_REAL'], self.node.traits)
        node = self.operator_cloud.baremetal.get_node(self.node)
        self.assertEqual(['CUSTOM_REAL'], node.traits)

    def test_set_node_traits(self):
        node = self.operator_cloud.baremetal.get_node(self.node)
        self.assertEqual([], node.traits)

        traits1 = ['CUSTOM_FAKE', 'CUSTOM_REAL']
        traits2 = ['CUSTOM_FOOBAR']

        self.operator_cloud.baremetal.set_node_traits(self.node, traits1)
        self.assertEqual(sorted(traits1), sorted(self.node.traits))
        node = self.operator_cloud.baremetal.get_node(self.node)
        self.assertEqual(sorted(traits1), sorted(node.traits))

        self.operator_cloud.baremetal.set_node_traits(self.node, traits2)
        self.assertEqual(['CUSTOM_FOOBAR'], self.node.traits)
        node = self.operator_cloud.baremetal.get_node(self.node)
        self.assertEqual(['CUSTOM_FOOBAR'], node.traits)


class TestBareMetalNodeListFirmware(base.BaseBaremetalTest):
    min_microversion = '1.86'

    def test_list_firmware(self):
        node = self.create_node(firmware_interface="no-firmware")
        self.assertEqual("no-firmware", node.firmware_interface)
        result = self.operator_cloud.baremetal.list_node_firmware(node)
        self.assertEqual({'firmware': []}, result)
