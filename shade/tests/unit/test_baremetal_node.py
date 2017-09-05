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

"""
test_baremetal_node
----------------------------------

Tests for baremetal node related operations
"""

import uuid

from shade.tests import fakes
from shade.tests.unit import base


class TestBaremetalNode(base.IronicTestCase):

    def setUp(self):
        super(TestBaremetalNode, self).setUp()
        self.fake_baremetal_node = fakes.make_fake_machine(
            self.name, self.uuid)

    def test_list_machines(self):
        fake_baremetal_two = fakes.make_fake_machine('two', str(uuid.uuid4()))
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(resource='nodes'),
                 json={'nodes': [self.fake_baremetal_node,
                                 fake_baremetal_two]}),
        ])

        machines = self.op_cloud.list_machines()
        self.assertEqual(2, len(machines))
        self.assertEqual(self.fake_baremetal_node, machines[0])
        self.assert_calls()

    def test_get_machine(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     resource='nodes',
                     append=[self.fake_baremetal_node['uuid']]),
                 json=self.fake_baremetal_node),
        ])

        machine = self.op_cloud.get_machine(self.fake_baremetal_node['uuid'])
        self.assertEqual(machine['uuid'],
                         self.fake_baremetal_node['uuid'])
        self.assert_calls()
