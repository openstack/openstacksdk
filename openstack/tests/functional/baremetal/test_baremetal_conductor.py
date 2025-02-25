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


from openstack.tests.functional.baremetal import base


class TestBareMetalConductor(base.BaseBaremetalTest):
    min_microversion = '1.49'

    def test_list_get_conductor(self):
        node = self.create_node(name='node-name')
        conductors = self.operator_cloud.baremetal.conductors()
        hostname_list = [conductor.hostname for conductor in conductors]
        self.assertIn(node.conductor, hostname_list)
        conductor1 = self.operator_cloud.baremetal.get_conductor(
            node.conductor
        )
        self.assertIsNotNone(conductor1.conductor_group)
        self.assertIsNotNone(conductor1.links)
        self.assertTrue(conductor1.alive)
