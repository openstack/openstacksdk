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

from openstack.compute.v2 import server
from openstack.tests.functional import base
from openstack.tests.functional.network.v2 import test_network

# TODO(thowe): These values should be able to be set in clouds.yaml
default_flavor = '2'
default_image = 'cirros-0.3.4-x86_64-uec'


class TestServer(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    server = None
    network = None
    subnet = None

    @classmethod
    def setUpClass(cls):
        super(TestServer, cls).setUpClass()
        flavor = default_flavor
        image = cls.conn.compute.find_image(default_image)
        cls.network, cls.subnet = test_network.create_network(cls.conn,
                                                              cls.NAME)
        if cls.network:
            args = {'networks': [{"uuid": cls.network.id}]}
        else:
            args = {}
        sot = cls.conn.compute.create_server(
            name=cls.NAME, flavor=flavor, image=image.id, **args)
        assert isinstance(sot, server.Server)
        cls.assertIs(cls.NAME, sot.name)
        cls.server = sot

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.compute.delete_server(cls.server.id)
        cls.assertIs(None, sot)
        # Need to wait for the stack to go away before network delete
        cls.conn.compute.wait_for_delete(cls.server)
        cls.linger_for_delete()
        test_network.delete_network(cls.conn, cls.network, cls.subnet)

    def test_find(self):
        sot = self.conn.compute.find_server(self.NAME)
        self.assertEqual(self.server.id, sot.id)

    def test_get(self):
        sot = self.conn.compute.get_server(self.server.id)
        self.assertEqual(self.NAME, sot.name)
        self.assertEqual(self.server.id, sot.id)

    def test_list(self):
        names = [o.name for o in self.conn.compute.servers()]
        self.assertIn(self.NAME, names)
