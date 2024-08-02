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

from openstack.network.v2 import agent
from openstack.network.v2 import network
from openstack.tests.functional import base


class TestAgentNetworks(base.BaseFunctionalTest):
    NETWORK_ID: str
    AGENT: agent.Agent
    AGENT_ID: str

    def setUp(self):
        super().setUp()
        if not self.user_cloud._has_neutron_extension("agent"):
            self.skipTest("Neutron agent extension is required for this test")

        self.NETWORK_NAME = self.getUniqueString("network")
        net = self.user_cloud.network.create_network(name=self.NETWORK_NAME)
        self.addCleanup(self.user_cloud.network.delete_network, net.id)
        assert isinstance(net, network.Network)
        self.NETWORK_ID = net.id
        agent_list = list(self.user_cloud.network.agents())
        agents = [
            agent for agent in agent_list if agent.agent_type == "DHCP agent"
        ]
        if len(agent_list) == 0:
            self.skipTest("No agents available")

        self.AGENT = agents[0]
        self.AGENT_ID = self.AGENT.id

    def test_add_remove_agent(self):
        net = self.AGENT.add_agent_to_network(
            self.user_cloud.network, network_id=self.NETWORK_ID
        )
        self._verify_add(net)

        net = self.AGENT.remove_agent_from_network(
            self.user_cloud.network, network_id=self.NETWORK_ID
        )
        self._verify_remove(net)

    def _verify_add(self, network):
        net = self.user_cloud.network.dhcp_agent_hosting_networks(
            self.AGENT_ID
        )
        net_ids = [n.id for n in net]
        self.assertIn(self.NETWORK_ID, net_ids)

    def _verify_remove(self, network):
        net = self.user_cloud.network.dhcp_agent_hosting_networks(
            self.AGENT_ID
        )
        net_ids = [n.id for n in net]
        self.assertNotIn(self.NETWORK_ID, net_ids)
