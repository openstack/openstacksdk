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


from openstack import exceptions
from openstack.tests.functional.baremetal import base


class TestBareMetalVolumetarget(base.BaseBaremetalTest):

    min_microversion = '1.32'

    def setUp(self):
        super(TestBareMetalVolumetarget, self).setUp()
        self.node = self.create_node(provision_state='enroll')

    def test_volume_target_create_get_delete(self):
        self.conn.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True)
        self.conn.baremetal.set_node_power_state(self.node, 'power off')
        volume_target = self.create_volume_target(
            boot_index=0,
            volume_id='04452bed-5367-4202-8bf5-de4335ac56d2',
            volume_type='iscsi')

        loaded = self.conn.baremetal.get_volume_target(
            volume_target.id)
        self.assertEqual(loaded.id, volume_target.id)
        self.assertIsNotNone(loaded.node_id)

        with_fields = self.conn.baremetal.get_volume_target(
            volume_target.id, fields=['uuid', 'extra'])
        self.assertEqual(volume_target.id, with_fields.id)
        self.assertIsNone(with_fields.node_id)

        self.conn.baremetal.delete_volume_target(volume_target,
                                                 ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_volume_target,
                          volume_target.id)

    def test_volume_target_list(self):
        node2 = self.create_node(name='test-node')
        self.conn.baremetal.set_node_provision_state(
            node2, 'manage', wait=True)
        self.conn.baremetal.set_node_power_state(node2, 'power off')
        self.conn.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True)
        self.conn.baremetal.set_node_power_state(self.node, 'power off')
        vt1 = self.create_volume_target(
            boot_index=0,
            volume_id='bd4d008c-7d31-463d-abf9-6c23d9d55f7f',
            node_id=node2.id,
            volume_type='iscsi')
        vt2 = self.create_volume_target(
            boot_index=0,
            volume_id='04452bed-5367-4202-8bf5-de4335ac57c2',
            node_id=self.node.id,
            volume_type='iscsi')

        vts = self.conn.baremetal.volume_targets(
            node=self.node.id)
        self.assertEqual([v.id for v in vts], [vt2.id])

        vts = self.conn.baremetal.volume_targets(node=node2.id)
        self.assertEqual([v.id for v in vts], [vt1.id])

        vts = self.conn.baremetal.volume_targets(node='test-node')
        self.assertEqual([v.id for v in vts], [vt1.id])

        vts_with_details = self.conn.baremetal.volume_targets(details=True)
        for i in vts_with_details:
            self.assertIsNotNone(i.id)
            self.assertIsNotNone(i.volume_type)

        vts_with_fields = self.conn.baremetal.volume_targets(
            fields=['uuid', 'node_uuid'])
        for i in vts_with_fields:
            self.assertIsNotNone(i.id)
            self.assertIsNone(i.volume_type)
            self.assertIsNotNone(i.node_id)

    def test_volume_target_list_update_delete(self):
        self.conn.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True)
        self.conn.baremetal.set_node_power_state(self.node, 'power off')
        self.create_volume_target(
            boot_index=0,
            volume_id='04452bed-5367-4202-8bf5-de4335ac57h3',
            node_id=self.node.id,
            volume_type='iscsi',
            extra={'foo': 'bar'})
        volume_target = next(self.conn.baremetal.volume_targets(
            details=True,
            node=self.node.id))
        self.assertEqual(volume_target.extra, {'foo': 'bar'})

        # This test checks that resources returned from listing are usable
        self.conn.baremetal.update_volume_target(volume_target,
                                                 extra={'foo': 42})
        self.conn.baremetal.delete_volume_target(volume_target,
                                                 ignore_missing=False)

    def test_volume_target_update(self):
        self.conn.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True)
        self.conn.baremetal.set_node_power_state(self.node, 'power off')
        volume_target = self.create_volume_target(
            boot_index=0,
            volume_id='04452bed-5367-4202-8bf5-de4335ac53h7',
            node_id=self.node.id,
            volume_type='isci')
        volume_target.extra = {'answer': 42}

        volume_target = self.conn.baremetal.update_volume_target(
            volume_target)
        self.assertEqual({'answer': 42}, volume_target.extra)

        volume_target = self.conn.baremetal.get_volume_target(
            volume_target.id)
        self.assertEqual({'answer': 42}, volume_target.extra)

    def test_volume_target_patch(self):
        vol_targ_id = '04452bed-5367-4202-9cg6-de4335ac53h7'
        self.conn.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True)
        self.conn.baremetal.set_node_power_state(self.node, 'power off')
        volume_target = self.create_volume_target(
            boot_index=0,
            volume_id=vol_targ_id,
            node_id=self.node.id,
            volume_type='isci')

        volume_target = self.conn.baremetal.patch_volume_target(
            volume_target, dict(path='/extra/answer', op='add', value=42))
        self.assertEqual({'answer': 42}, volume_target.extra)
        self.assertEqual(vol_targ_id,
                         volume_target.volume_id)

        volume_target = self.conn.baremetal.get_volume_target(
            volume_target.id)
        self.assertEqual({'answer': 42}, volume_target.extra)

    def test_volume_target_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_volume_target, uuid)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.find_volume_target, uuid,
                          ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.delete_volume_target, uuid,
                          ignore_missing=False)
        self.assertIsNone(self.conn.baremetal.find_volume_target(uuid))
        self.assertIsNone(self.conn.baremetal.delete_volume_target(uuid))

    def test_volume_target_fields(self):
        self.create_node()
        self.conn.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True)
        self.conn.baremetal.set_node_power_state(self.node, 'power off')
        self.create_volume_target(
            boot_index=0,
            volume_id='04452bed-5367-4202-8bf5-99ae634d8971',
            node_id=self.node.id,
            volume_type='iscsi')
        result = self.conn.baremetal.volume_targets(
            fields=['uuid', 'node_id'])
        for item in result:
            self.assertIsNotNone(item.id)
