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


class TestServer(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    server = None
    network = None
    subnet = None
    cidr = '10.99.99.0/16'

    @classmethod
    def setUpClass(cls):
        super(TestServer, cls).setUpClass()
        flavor = cls.conn.compute.find_flavor(base.FLAVOR_NAME,
                                              ignore_missing=False)
        image = cls.conn.compute.find_image(base.IMAGE_NAME,
                                            ignore_missing=False)
        cls.network, cls.subnet = test_network.create_network(cls.conn,
                                                              cls.NAME,
                                                              cls.cidr)
        if cls.network:
            args = {'networks': [{"uuid": cls.network.id}]}
        else:
            args = {}
        sot = cls.conn.compute.create_server(
            name=cls.NAME, flavor_id=flavor.id, image_id=image.id, **args)
        cls.conn.compute.wait_for_server(sot)
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

    def test_server_metadata(self):
        test_server = self.conn.compute.get_server(self.server.id)

        # get metadata
        test_server = self.conn.compute.get_server_metadata(test_server)
        self.assertFalse(test_server.metadata)

        # set no metadata
        self.conn.compute.set_server_metadata(test_server)
        test_server = self.conn.compute.get_server_metadata(test_server)
        self.assertFalse(test_server.metadata)

        # set empty metadata
        self.conn.compute.set_server_metadata(test_server, k0='')
        server = self.conn.compute.get_server_metadata(test_server)
        self.assertTrue(server.metadata)

        # set metadata
        self.conn.compute.set_server_metadata(test_server, k1='v1')
        test_server = self.conn.compute.get_server_metadata(test_server)
        self.assertTrue(test_server.metadata)
        self.assertEqual(2, len(test_server.metadata))
        self.assertIn('k0', test_server.metadata)
        self.assertEqual('', test_server.metadata['k0'])
        self.assertIn('k1', test_server.metadata)
        self.assertEqual('v1', test_server.metadata['k1'])

        # set more metadata
        self.conn.compute.set_server_metadata(test_server, k2='v2')
        test_server = self.conn.compute.get_server_metadata(test_server)
        self.assertTrue(test_server.metadata)
        self.assertEqual(3, len(test_server.metadata))
        self.assertIn('k0', test_server.metadata)
        self.assertEqual('', test_server.metadata['k0'])
        self.assertIn('k1', test_server.metadata)
        self.assertEqual('v1', test_server.metadata['k1'])
        self.assertIn('k2', test_server.metadata)
        self.assertEqual('v2', test_server.metadata['k2'])

        # update metadata
        self.conn.compute.set_server_metadata(test_server, k1='v1.1')
        test_server = self.conn.compute.get_server_metadata(test_server)
        self.assertTrue(test_server.metadata)
        self.assertEqual(3, len(test_server.metadata))
        self.assertIn('k0', test_server.metadata)
        self.assertEqual('', test_server.metadata['k0'])
        self.assertIn('k1', test_server.metadata)
        self.assertEqual('v1.1', test_server.metadata['k1'])
        self.assertIn('k2', test_server.metadata)
        self.assertEqual('v2', test_server.metadata['k2'])

        # delete metadata
        self.conn.compute.delete_server_metadata(
            test_server, test_server.metadata.keys())
        test_server = self.conn.compute.get_server_metadata(test_server)
        self.assertFalse(test_server.metadata)
