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

from openstack.network.v2 import agent
from openstack.tests.functional import base


class TestAgent(base.BaseFunctionalTest):

    AGENT = None
    DESC = 'test descrition'

    def validate_uuid(self, s):
        try:
            uuid.UUID(s)
        except Exception:
            return False
        return True

    def setUp(self):
        super(TestAgent, self).setUp()
        agent_list = list(self.conn.network.agents())
        self.AGENT = agent_list[0]
        assert isinstance(self.AGENT, agent.Agent)

    def test_list(self):
        agent_list = list(self.conn.network.agents())
        self.AGENT = agent_list[0]
        assert isinstance(self.AGENT, agent.Agent)
        self.assertTrue(self.validate_uuid(self.AGENT.id))

    def test_get(self):
        sot = self.conn.network.get_agent(self.AGENT.id)
        self.assertEqual(self.AGENT.id, sot.id)

    def test_update(self):
        sot = self.conn.network.update_agent(self.AGENT.id,
                                             description=self.DESC)
        self.assertEqual(self.DESC, sot.description)
