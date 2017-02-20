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

from openstack.network.v2 import network
from openstack.tests.functional import base


class TestAgentNetworks(base.BaseFunctionalTest):

    NETWORK_NAME = 'network-' + uuid.uuid4().hex
    NETWORK_ID = None
    AGENT = None
    AGENT_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestAgentNetworks, cls).setUpClass()

        net = cls.conn.network.create_network(name=cls.NETWORK_NAME)
        assert isinstance(net, network.Network)
        cls.NETWORK_ID = net.id
        agent_list = list(cls.conn.network.agents())
        agents = [agent for agent in agent_list
                  if agent.agent_type == 'DHCP agent']
        cls.AGENT = agents[0]
        cls.AGENT_ID = cls.AGENT.id

    @classmethod
    def tearDownClass(cls):
        cls.conn.network.delete_network(cls.NETWORK_ID)

    def test_add_agent_to_network(self):
        net = self.AGENT.add_agent_to_network(self.conn.session,
                                              network_id=self.NETWORK_ID)
        self._verify_add(net)

    def test_remove_agent_from_network(self):
        net = self.AGENT.remove_agent_from_network(self.conn.session,
                                                   network_id=self.NETWORK_ID)
        self._verify_remove(net)

    def _verify_add(self, network):
        net = self.conn.network.dhcp_agent_hosting_networks(self.AGENT_ID)
        net_ids = [n.id for n in net]
        self.assertIn(self.NETWORK_ID, net_ids)

    def _verify_remove(self, network):
        net = self.conn.network.dhcp_agent_hosting_networks(self.AGENT_ID)
        net_ids = [n.id for n in net]
        self.assertNotIn(self.NETWORK_ID, net_ids)
