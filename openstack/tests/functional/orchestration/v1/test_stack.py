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

    _wait_for_timeout_key = 'OPENSTACKSDK_FUNC_TEST_TIMEOUT_ORCHESTRATION'

    def setUp(self):
        super().setUp()
        self.require_service('orchestration')

        if self.operator_cloud.compute.find_keypair(self.NAME) is None:
            self.operator_cloud.compute.create_keypair(name=self.NAME)
        image = next(self.operator_cloud.image.images())
        tname = "openstack/tests/functional/orchestration/v1/hello_world.yaml"
        with open(tname) as f:
            template = yaml.safe_load(f)
        # TODO(mordred) Fix the need for this. We have better support in
        # the shade layer.
        template['heat_template_version'] = '2013-05-23'
        self.network, self.subnet = test_network.create_network(
            self.operator_cloud, self.NAME, self.cidr
        )
        parameters = {
            'image': image.id,
            'key_name': self.NAME,
            'network': self.network.id,
        }
        sot = self.operator_cloud.orchestration.create_stack(
            name=self.NAME,
            parameters=parameters,
            template=template,
        )
        assert isinstance(sot, stack.Stack)
        self.assertEqual(True, (sot.id is not None))
        self.stack = sot
        self.assertEqual(self.NAME, sot.name)
        self.operator_cloud.orchestration.wait_for_status(
            sot,
            status='CREATE_COMPLETE',
            failures=['CREATE_FAILED'],
            wait=self._wait_for_timeout,
        )

    def tearDown(self):
        self.operator_cloud.orchestration.delete_stack(
            self.stack, ignore_missing=False
        )
        self.operator_cloud.compute.delete_keypair(self.NAME)
        # Need to wait for the stack to go away before network delete
        try:
            self.operator_cloud.orchestration.wait_for_status(
                self.stack, 'DELETE_COMPLETE', wait=self._wait_for_timeout
            )
        except exceptions.NotFoundException:
            pass
        test_network.delete_network(
            self.operator_cloud, self.network, self.subnet
        )
        super().tearDown()

    def test_list(self):
        names = [o.name for o in self.operator_cloud.orchestration.stacks()]
        self.assertIn(self.NAME, names)

    def test_suspend_resume(self):
        # given
        suspend_status = "SUSPEND_COMPLETE"
        resume_status = "RESUME_COMPLETE"

        # when
        self.operator_cloud.orchestration.suspend_stack(self.stack)
        sot = self.operator_cloud.orchestration.wait_for_status(
            self.stack, suspend_status, wait=self._wait_for_timeout
        )

        # then
        self.assertEqual(suspend_status, sot.status)

        # when
        self.operator_cloud.orchestration.resume_stack(self.stack)
        sot = self.operator_cloud.orchestration.wait_for_status(
            self.stack, resume_status, wait=self._wait_for_timeout
        )

        # then
        self.assertEqual(resume_status, sot.status)
