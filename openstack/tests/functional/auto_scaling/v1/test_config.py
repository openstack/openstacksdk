#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import uuid

from openstack.tests.functional import base


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
        # cls.network, cls.subnet = test_network.create_network(cls.conn,
        #                                                       cls.NAME,
        #                                                       cls.cidr)
        # if not cls.network:
        #     # We can't call TestCase.fail from within the setUpClass
        #     # classmethod, but we need to raise some exception in order
        #     # to get this setup to fail and thusly fail the entire class.
        #     raise Exception("Unable to create network for TestServer")
        #
        # sot = cls.conn.compute.create_server(
        #     name=cls.NAME, flavor_id=flavor.id, image_id=image.id,
        #     networks=[{"uuid": cls.network.id}])
        # cls.conn.compute.wait_for_server(sot)
        # assert isinstance(sot, server.Server)
        # cls.assertIs(cls.NAME, sot.name)
        # cls.server = sot

    def test_list_config(self):
        pass
