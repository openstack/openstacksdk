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
        sot = self.conn.compute.get_server(self.server.id)

        # Start by clearing out any other metadata.
        self.assertDictEqual(self.conn.compute.replace_server_metadata(sot),
                             {})

        # Create first and last name metadata
        meta = {"first": "Matthew", "last": "Dellavedova"}
        self.assertDictEqual(
            self.conn.compute.create_server_metadata(sot, **meta), meta)

        # Create something that already exists
        meta = {"last": "Inman"}
        self.assertDictEqual(
            self.conn.compute.create_server_metadata(sot, **meta), meta)

        # Update only the first name
        short = {"first": "Matt", "last": "Inman"}
        self.assertDictEqual(
            self.conn.compute.update_server_metadata(sot,
                                                     first=short["first"]),
            short)

        # Get all metadata and then only the last name
        self.assertDictEqual(self.conn.compute.get_server_metadata(sot),
                             short)
        self.assertDictEqual(
            self.conn.compute.get_server_metadata(sot, "last"),
            {"last": short["last"]})

        # Replace everything with just a nickname
        nick = {"nickname": "Delly"}
        self.assertDictEqual(
            self.conn.compute.replace_server_metadata(sot, **nick),
            nick)
        self.assertDictEqual(self.conn.compute.get_server_metadata(sot),
                             nick)

        # Delete the only remaining key, make sure we're empty
        self.assertIsNone(
            self.conn.compute.delete_server_metadata(sot, "nickname"))
        self.assertDictEqual(self.conn.compute.get_server_metadata(sot), {})
