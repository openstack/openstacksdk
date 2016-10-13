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

from openstack.network.v2 import router
from openstack.tests.functional import base


class TestAgentRouters(base.BaseFunctionalTest):

    ROUTER_NAME = 'router-name-' + uuid.uuid4().hex
    ROUTER_ID = None
    AGENT = None
    AGENT_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestAgentRouters, cls).setUpClass()

        rot = cls.conn.network.create_router(name=cls.ROUTER_NAME)
        assert isinstance(rot, router.Router)
        cls.ROUTER_ID = rot.id
        agent_list = list(cls.conn.network.agents())
        agents = [agent for agent in agent_list
                  if agent.agent_type == 'L3 agent']
        cls.AGENT = agents[0]
        cls.AGENT_ID = cls.AGENT.id

    @classmethod
    def tearDownClass(cls):
        rot = cls.conn.network.delete_router(cls.ROUTER_ID,
                                             ignore_missing=False)
        cls.assertIs(None, rot)

    def test_add_router_to_agent(self):
        sot = self.AGENT.add_router_to_agent(self.conn.session,
                                             router_id=self.ROUTER_ID)
        self._verify_add(sot)

    def test_remove_router_from_agent(self):
        sot = self.AGENT.remove_router_from_agent(self.conn.session,
                                                  router_id=self.ROUTER_ID)
        self._verify_remove(sot)

    def _verify_add(self, sot):
        rots = self.conn.network.agent_hosted_routers(self.AGENT_ID)
        routers = [router.id for router in rots]
        self.assertIn(self.ROUTER_ID, routers)

    def _verify_remove(self, sot):
        rots = self.conn.network.agent_hosted_routers(self.AGENT_ID)
        routers = [router.id for router in rots]
        self.assertNotIn(self.ROUTER_ID, routers)
