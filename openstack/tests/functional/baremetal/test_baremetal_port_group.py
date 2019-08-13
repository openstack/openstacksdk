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


class TestBareMetalPortGroup(base.BaseBaremetalTest):

    min_microversion = '1.23'

    def setUp(self):
        super(TestBareMetalPortGroup, self).setUp()
        self.node = self.create_node()

    def test_port_group_create_get_delete(self):
        port_group = self.create_port_group()

        loaded = self.conn.baremetal.get_port_group(port_group.id)
        self.assertEqual(loaded.id, port_group.id)
        self.assertIsNotNone(loaded.node_id)

        with_fields = self.conn.baremetal.get_port_group(
            port_group.id, fields=['uuid', 'extra'])
        self.assertEqual(port_group.id, with_fields.id)
        self.assertIsNone(with_fields.node_id)

        self.conn.baremetal.delete_port_group(port_group,
                                              ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_port_group, port_group.id)

    def test_port_list(self):
        node2 = self.create_node(name='test-node')

        pg1 = self.create_port_group(address='11:22:33:44:55:66',
                                     node_id=node2.id)
        pg2 = self.create_port_group(address='11:22:33:44:55:77',
                                     node_id=self.node.id)

        pgs = self.conn.baremetal.port_groups(address='11:22:33:44:55:77')
        self.assertEqual([p.id for p in pgs], [pg2.id])

        pgs = self.conn.baremetal.port_groups(node=node2.id)
        self.assertEqual([p.id for p in pgs], [pg1.id])

        pgs = self.conn.baremetal.port_groups(node='test-node')
        self.assertEqual([p.id for p in pgs], [pg1.id])

    def test_port_list_update_delete(self):
        self.create_port_group(address='11:22:33:44:55:66',
                               extra={'foo': 'bar'})
        port_group = next(self.conn.baremetal.port_groups(
            details=True, address='11:22:33:44:55:66'))
        self.assertEqual(port_group.extra, {'foo': 'bar'})

        # This test checks that resources returned from listing are usable
        self.conn.baremetal.update_port_group(port_group, extra={'foo': 42})
        self.conn.baremetal.delete_port_group(port_group, ignore_missing=False)

    def test_port_group_update(self):
        port_group = self.create_port_group()
        port_group.extra = {'answer': 42}

        port_group = self.conn.baremetal.update_port_group(port_group)
        self.assertEqual({'answer': 42}, port_group.extra)

        port_group = self.conn.baremetal.get_port_group(port_group.id)
        self.assertEqual({'answer': 42}, port_group.extra)

    def test_port_group_patch(self):
        port_group = self.create_port_group()

        port_group = self.conn.baremetal.patch_port_group(
            port_group, dict(path='/extra/answer', op='add', value=42))
        self.assertEqual({'answer': 42}, port_group.extra)

        port_group = self.conn.baremetal.get_port_group(port_group.id)
        self.assertEqual({'answer': 42}, port_group.extra)

    def test_port_group_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.get_port_group, uuid)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.find_port_group, uuid,
                          ignore_missing=False)
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.baremetal.delete_port_group, uuid,
                          ignore_missing=False)
        self.assertIsNone(self.conn.baremetal.find_port_group(uuid))
        self.assertIsNone(self.conn.baremetal.delete_port_group(uuid))

    def test_port_group_fields(self):
        self.create_node()
        self.create_port_group(address='11:22:33:44:55:66')
        result = self.conn.baremetal.port_groups(fields=['uuid', 'name'])
        for item in result:
            self.assertIsNotNone(item.id)
            self.assertIsNone(item.address)
