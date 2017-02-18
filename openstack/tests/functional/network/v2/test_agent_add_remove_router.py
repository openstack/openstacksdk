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
    ROUTER = None
    AGENT = None

    @classmethod
    def setUpClass(cls):
        super(TestAgentRouters, cls).setUpClass()

        cls.ROUTER = cls.conn.network.create_router(name=cls.ROUTER_NAME)
        assert isinstance(cls.ROUTER, router.Router)
        agent_list = list(cls.conn.network.agents())
        agents = [agent for agent in agent_list
                  if agent.agent_type == 'L3 agent']
        cls.AGENT = agents[0]

    @classmethod
    def tearDownClass(cls):
        cls.conn.network.delete_router(cls.ROUTER)

    def test_add_router_to_agent(self):
        self.conn.network.add_router_to_agent(self.AGENT, self.ROUTER)
        rots = self.conn.network.agent_hosted_routers(self.AGENT)
        routers = [router.id for router in rots]
        self.assertIn(self.ROUTER.id, routers)

    def test_remove_router_from_agent(self):
        self.conn.network.remove_router_from_agent(self.AGENT, self.ROUTER)
        rots = self.conn.network.agent_hosted_routers(self.AGENT)
        routers = [router.id for router in rots]
        self.assertNotIn(self.ROUTER.id, routers)
