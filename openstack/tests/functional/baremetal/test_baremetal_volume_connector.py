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


class TestBareMetalVolumeconnector(base.BaseBaremetalTest):
    min_microversion = '1.32'

    def setUp(self):
        super().setUp()
        self.node = self.create_node(provision_state='enroll')

    def test_volume_connector_create_get_delete(self):
        self.operator_cloud.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_power_state(
            self.node, 'power off'
        )
        volume_connector = self.create_volume_connector(
            connector_id='iqn.2017-07.org.openstack:01:d9a51732c3f', type='iqn'
        )

        loaded = self.operator_cloud.baremetal.get_volume_connector(
            volume_connector.id
        )
        self.assertEqual(loaded.id, volume_connector.id)
        self.assertIsNotNone(loaded.node_id)

        with_fields = self.operator_cloud.baremetal.get_volume_connector(
            volume_connector.id, fields=['uuid', 'extra']
        )
        self.assertEqual(volume_connector.id, with_fields.id)
        self.assertIsNone(with_fields.node_id)

        self.operator_cloud.baremetal.delete_volume_connector(
            volume_connector, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_volume_connector,
            volume_connector.id,
        )

    def test_volume_connector_list(self):
        node2 = self.create_node(name='test-node')
        self.operator_cloud.baremetal.set_node_provision_state(
            node2, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_power_state(node2, 'power off')
        self.operator_cloud.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_power_state(
            self.node, 'power off'
        )
        vc1 = self.create_volume_connector(
            connector_id='iqn.2018-07.org.openstack:01:d9a514g2c32',
            node_id=node2.id,
            type='iqn',
        )
        vc2 = self.create_volume_connector(
            connector_id='iqn.2017-07.org.openstack:01:d9a51732c4g',
            node_id=self.node.id,
            type='iqn',
        )

        vcs = self.operator_cloud.baremetal.volume_connectors(
            node=self.node.id
        )
        self.assertEqual([v.id for v in vcs], [vc2.id])

        vcs = self.operator_cloud.baremetal.volume_connectors(node=node2.id)
        self.assertEqual([v.id for v in vcs], [vc1.id])

        vcs = self.operator_cloud.baremetal.volume_connectors(node='test-node')
        self.assertEqual([v.id for v in vcs], [vc1.id])

    def test_volume_connector_list_update_delete(self):
        self.operator_cloud.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_power_state(
            self.node, 'power off'
        )
        self.create_volume_connector(
            connector_id='iqn.2020-07.org.openstack:02:d9451472ce2',
            node_id=self.node.id,
            type='iqn',
            extra={'foo': 'bar'},
        )
        volume_connector = next(
            self.operator_cloud.baremetal.volume_connectors(
                details=True, node=self.node.id
            )
        )
        self.assertEqual(volume_connector.extra, {'foo': 'bar'})

        # This test checks that resources returned from listing are usable
        self.operator_cloud.baremetal.update_volume_connector(
            volume_connector, extra={'foo': 42}
        )
        self.operator_cloud.baremetal.delete_volume_connector(
            volume_connector, ignore_missing=False
        )

    def test_volume_connector_update(self):
        self.operator_cloud.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_power_state(
            self.node, 'power off'
        )
        volume_connector = self.create_volume_connector(
            connector_id='iqn.2019-07.org.openstack:03:de45b472c40',
            node_id=self.node.id,
            type='iqn',
        )
        volume_connector.extra = {'answer': 42}

        volume_connector = (
            self.operator_cloud.baremetal.update_volume_connector(
                volume_connector
            )
        )
        self.assertEqual({'answer': 42}, volume_connector.extra)

        volume_connector = self.operator_cloud.baremetal.get_volume_connector(
            volume_connector.id
        )
        self.assertEqual({'answer': 42}, volume_connector.extra)

    def test_volume_connector_patch(self):
        vol_conn_id = 'iqn.2020-07.org.openstack:04:de45b472c40'
        self.operator_cloud.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_power_state(
            self.node, 'power off'
        )
        volume_connector = self.create_volume_connector(
            connector_id=vol_conn_id, node_id=self.node.id, type='iqn'
        )

        volume_connector = (
            self.operator_cloud.baremetal.patch_volume_connector(
                volume_connector,
                dict(path='/extra/answer', op='add', value=42),
            )
        )
        self.assertEqual({'answer': 42}, volume_connector.extra)
        self.assertEqual(vol_conn_id, volume_connector.connector_id)

        volume_connector = self.operator_cloud.baremetal.get_volume_connector(
            volume_connector.id
        )
        self.assertEqual({'answer': 42}, volume_connector.extra)

    def test_volume_connector_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_volume_connector,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.find_volume_connector,
            uuid,
            ignore_missing=False,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.delete_volume_connector,
            uuid,
            ignore_missing=False,
        )
        self.assertIsNone(
            self.operator_cloud.baremetal.find_volume_connector(uuid)
        )
        self.assertIsNone(
            self.operator_cloud.baremetal.delete_volume_connector(uuid)
        )

    def test_volume_connector_fields(self):
        self.create_node()
        self.operator_cloud.baremetal.set_node_provision_state(
            self.node, 'manage', wait=True
        )
        self.operator_cloud.baremetal.set_node_power_state(
            self.node, 'power off'
        )
        self.create_volume_connector(
            connector_id='iqn.2018-08.org.openstack:04:de45f37c48',
            node_id=self.node.id,
            type='iqn',
        )
        result = self.operator_cloud.baremetal.volume_connectors(
            fields=['uuid', 'node_id']
        )
        for item in result:
            self.assertIsNotNone(item.id)
            self.assertIsNone(item.connector_id)
