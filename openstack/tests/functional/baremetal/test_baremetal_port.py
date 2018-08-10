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


class TestBareMetalPort(base.BaseBaremetalTest):

    def setUp(self):
        super(TestBareMetalPort, self).setUp()
        self.node = self.create_node()

    def test_port_create_get_delete(self):
        port = self.create_port(address='11:22:33:44:55:66')
        self.assertEqual(self.node_id, port.node_id)
        # Can be None if the microversion is too small, so we make sure it is
        # not False.
        self.assertNotEqual(port.is_pxe_enabled, False)
        self.assertIsNone(port.port_group_id)

        loaded = self.conn.baremetal.get_port(port.id)
        self.assertEqual(loaded.id, port.id)

        self.conn.baremetal.delete_port(port, ignore_missing=False)
        self.assertRaises(exceptions.NotFoundException,
                          self.conn.baremetal.get_port, port.id)

    def test_port_update(self):
        port = self.create_port(address='11:22:33:44:55:66')
        port.address = '66:55:44:33:22:11'
        port.extra = {'answer': 42}

        port = self.conn.baremetal.update_port(port)
        self.assertEqual('66:55:44:33:22:11', port.address)
        self.assertEqual({'answer': 42}, port.extra)

        port = self.conn.baremetal.get_port(port.id)
        self.assertEqual('66:55:44:33:22:11', port.address)
        self.assertEqual({'answer': 42}, port.extra)

    def test_port_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(exceptions.NotFoundException,
                          self.conn.baremetal.get_port, uuid)
        self.assertRaises(exceptions.NotFoundException,
                          self.conn.baremetal.find_port, uuid,
                          ignore_missing=False)
        self.assertRaises(exceptions.NotFoundException,
                          self.conn.baremetal.delete_port, uuid,
                          ignore_missing=False)
        self.assertRaises(exceptions.NotFoundException,
                          self.conn.baremetal.update_port, uuid,
                          pxe_enabled=True)
        self.assertIsNone(self.conn.baremetal.find_port(uuid))
        self.assertIsNone(self.conn.baremetal.delete_port(uuid))
