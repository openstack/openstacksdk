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

import os
import yaml

from openstack import exceptions
from openstack.orchestration.v1 import stack
from openstack.tests.functional import base
from openstack.tests.functional.network.v2 import test_network


class TestStack(base.BaseFunctionalTest):

    NAME = 'test_stack'
    stack = None
    network = None
    subnet = None
    cidr = '10.99.99.0/16'

    @classmethod
    def setUpClass(cls):
        super(TestStack, cls).setUpClass()
        cls._wait_for_timeout = int(os.getenv(
            'OPENSTACKSDK_FUNC_TEST_TIMEOUT_ORCHESTRATION',
            cls._wait_for_timeout))

    def setUp(self):
        super(TestStack, self).setUp()
        self.require_service('orchestration')

        if self.conn.compute.find_keypair(self.NAME) is None:
            self.conn.compute.create_keypair(name=self.NAME)
        image = next(self.conn.image.images())
        tname = "openstack/tests/functional/orchestration/v1/hello_world.yaml"
        with open(tname) as f:
            template = yaml.safe_load(f)
        # TODO(mordred) Fix the need for this. We have better support in
        # the shade layer.
        template['heat_template_version'] = '2013-05-23'
        self.network, self.subnet = test_network.create_network(
            self.conn,
            self.NAME,
            self.cidr)
        parameters = {
            'image': image.id,
            'key_name': self.NAME,
            'network': self.network.id,
        }
        sot = self.conn.orchestration.create_stack(
            name=self.NAME,
            parameters=parameters,
            template=template,
        )
        assert isinstance(sot, stack.Stack)
        self.assertEqual(True, (sot.id is not None))
        self.stack = sot
        self.assertEqual(self.NAME, sot.name)
        self.conn.orchestration.wait_for_status(
            sot, status='CREATE_COMPLETE', failures=['CREATE_FAILED'],
            wait=self._wait_for_timeout)

    def tearDown(self):
        self.conn.orchestration.delete_stack(self.stack, ignore_missing=False)
        self.conn.compute.delete_keypair(self.NAME)
        # Need to wait for the stack to go away before network delete
        try:
            self.conn.orchestration.wait_for_status(
                self.stack, 'DELETE_COMPLETE', wait=self._wait_for_timeout)
        except exceptions.ResourceNotFound:
            pass
        test_network.delete_network(self.conn, self.network, self.subnet)
        super(TestStack, self).tearDown()

    def test_list(self):
        names = [o.name for o in self.conn.orchestration.stacks()]
        self.assertIn(self.NAME, names)
