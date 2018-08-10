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

from openstack.tests.functional import base


class BaseBaremetalTest(base.BaseFunctionalTest):

    min_microversion = None
    node_id = None

    def setUp(self):
        super(BaseBaremetalTest, self).setUp()
        self.require_service('baremetal',
                             min_microversion=self.min_microversion)

    def create_chassis(self, **kwargs):
        chassis = self.conn.baremetal.create_chassis(**kwargs)
        self.addCleanup(
            lambda: self.conn.baremetal.delete_chassis(chassis.id,
                                                       ignore_missing=True))
        return chassis

    def create_node(self, driver='fake-hardware', **kwargs):
        node = self.conn.baremetal.create_node(driver=driver, **kwargs)
        self.node_id = node.id
        self.addCleanup(
            lambda: self.conn.baremetal.delete_node(self.node_id,
                                                    ignore_missing=True))
        self.assertIsNotNone(self.node_id)
        return node

    def create_port(self, node_id=None, **kwargs):
        node_id = node_id or self.node_id
        port = self.conn.baremetal.create_port(node_uuid=node_id, **kwargs)
        self.addCleanup(
            lambda: self.conn.baremetal.delete_port(port.id,
                                                    ignore_missing=True))
        return port

    def create_port_group(self, node_id=None, **kwargs):
        node_id = node_id or self.node_id
        port_group = self.conn.baremetal.create_port_group(node_uuid=node_id,
                                                           **kwargs)
        self.addCleanup(
            lambda: self.conn.baremetal.delete_port_group(port_group.id,
                                                          ignore_missing=True))
        return port_group
