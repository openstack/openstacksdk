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


class TestStack(base.BaseFunctionalTest):

    def test_create_stack(self):
        stack = self.conn.orchestration.create_stack(
            name='test_stack',
            parameters={'key_name': 'heat_key',
                        'image_id': 'fedora-20.x86_64'},
            template_url='http://git.openstack.org/cgit/openstack/' +
                         'heat-templates/plain/hot/F20/WordPress_Native.yaml'
        )

        self.conn.orchestration.wait_for_stack(stack)

        self.assertIsNotNone(stack.id)
        self.assertEqual('test_stack', stack.name)
