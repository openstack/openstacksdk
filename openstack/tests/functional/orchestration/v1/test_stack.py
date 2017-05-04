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

import unittest

from openstack import exceptions
from openstack.orchestration.v1 import stack
from openstack.tests.functional import base
from openstack.tests.functional.network.v2 import test_network


@unittest.skip("bug/1525005")
@unittest.skipUnless(base.service_exists(service_type='orchestration'),
                     'Orchestration service does not exist')
class TestStack(base.BaseFunctionalTest):

    NAME = 'test_stack'
    stack = None
    network = None
    subnet = None
    cidr = '10.99.99.0/16'

    @classmethod
    def setUpClass(cls):
        super(TestStack, cls).setUpClass()
        if cls.conn.compute.find_keypair(cls.NAME) is None:
            cls.conn.compute.create_keypair(name=cls.NAME)
        image = next(cls.conn.image.images())
        tname = "openstack/tests/functional/orchestration/v1/hello_world.yaml"
        with open(tname) as f:
            template = f.read()
        cls.network, cls.subnet = test_network.create_network(cls.conn,
                                                              cls.NAME,
                                                              cls.cidr)
        parameters = {
            'image': image.id,
            'key_name': cls.NAME,
            'network': cls.network.id,
        }
        sot = cls.conn.orchestration.create_stack(
            name=cls.NAME,
            parameters=parameters,
            template=template,
        )
        assert isinstance(sot, stack.Stack)
        cls.assertIs(True, (sot.id is not None))
        cls.stack = sot
        cls.assertIs(cls.NAME, sot.name)
        cls.conn.orchestration.wait_for_status(
            sot, status='CREATE_COMPLETE', failures=['CREATE_FAILED'])

    @classmethod
    def tearDownClass(cls):
        super(TestStack, cls).tearDownClass()
        cls.conn.orchestration.delete_stack(cls.stack, ignore_missing=False)
        cls.conn.compute.delete_keypair(cls.NAME)
        # Need to wait for the stack to go away before network delete
        try:
            cls.conn.orchestration.wait_for_status(
                cls.stack, 'DELETE_COMPLETE')
        except exceptions.NotFoundException:
            pass
        cls.linger_for_delete()
        test_network.delete_network(cls.conn, cls.network, cls.subnet)

    def test_list(self):
        names = [o.name for o in self.conn.orchestration.stacks()]
        self.assertIn(self.NAME, names)
