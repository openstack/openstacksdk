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

from openstack.orchestration.v1 import stack
from openstack.tests.functional import base


class TestStack(base.BaseFunctionalTest):

    NAME = 'test_stack'
    ID = None

    @classmethod
    def setUpClass(cls):
        super(TestStack, cls).setUpClass()
        if cls.conn.compute.find_keypair(cls.NAME) is None:
            cls.conn.compute.create_keypair(name=cls.NAME)
        template_url = ('http://git.openstack.org/cgit/openstack/' +
                        'heat-templates/plain/hot/F20/WordPress_Native.yaml')
        sot = cls.conn.orchestration.create_stack(
            name=cls.NAME,
            parameters={'key_name': cls.NAME, 'image_id': 'fedora-20.x86_64'},
            template_url=template_url,
        )
        assert isinstance(sot, stack.Stack)
        cls.assertIs(True, (sot.id is not None))
        cls.ID = sot.id
        cls.assertIs(cls.NAME, sot.name)
        cls.conn.orchestration.wait_for_stack(sot)

    @classmethod
    def tearDownClass(cls):
        super(TestStack, cls).tearDownClass()
        cls.conn.orchestration.delete_stack(cls.ID)
        cls.conn.compute.delete_keypair(cls.NAME)

    def test_list(self):
        names = [o.name for o in self.conn.orchestration.list_stacks()]
        self.assertIn(self.NAME, names)
