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


from openstack.network.v2 import router
from openstack.tests.functional import base


class TestAgentRouters(base.BaseFunctionalTest):

    ROUTER = None
    AGENT = None

    def setUp(self):
        super(TestAgentRouters, self).setUp()

        self.ROUTER_NAME = 'router-name-' + self.getUniqueString('router-name')
        self.ROUTER = self.conn.network.create_router(name=self.ROUTER_NAME)
        self.addCleanup(self.conn.network.delete_router, self.ROUTER)
        assert isinstance(self.ROUTER, router.Router)
        agent_list = list(self.conn.network.agents())
        agents = [agent for agent in agent_list
                  if agent.agent_type == 'L3 agent']
        self.AGENT = agents[0]

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
