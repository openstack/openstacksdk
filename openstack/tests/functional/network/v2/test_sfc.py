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

from openstack.network.v2 import network as _network
from openstack.network.v2 import port as _port
from openstack.network.v2 import sfc_flow_classifier as _flow_classifier
from openstack.network.v2 import subnet as _subnet
from openstack.tests.functional import base


class TestSFCFlowClassifier(base.BaseFunctionalTest):
    FC_ID = None

    def setUp(self):
        super().setUp()

        if not self.user_cloud.network.find_extension("sfc"):
            self.skipTest("Neutron SFC Extension disabled")

        self.FLOW_CLASSIFIER_NAME = 'my_classifier' + self.getUniqueString()
        self.UPDATE_NAME = 'updated' + self.getUniqueString()
        self.NET_NAME = 'network1' + self.getUniqueString()
        self.SUBNET_NAME = 'subnet1' + self.getUniqueString()
        self.PORT1_NAME = 'port1' + self.getUniqueString()
        self.PORT2_NAME = 'port2' + self.getUniqueString()
        self.ETHERTYPE = 'IPv4'
        self.PROTOCOL = 'tcp'
        self.S_PORT_RANGE_MIN = 80
        self.S_PORT_RANGE_MAX = 80
        self.D_PORT_RANGE_MIN = 180
        self.D_PORT_RANGE_MAX = 180
        self.CIDR = "10.101.0.0/24"
        self.SOURCE_IP = '10.101.1.12/32'
        self.DESTINATION_IP = '10.102.2.12/32'

        self.PORT_CHAIN_NAME = 'my_chain' + self.getUniqueString()
        self.PORT_PAIR_NAME = 'my_port_pair' + self.getUniqueString()
        self.PORT_PAIR_GROUP_NAME = (
            'my_port_pair_group' + self.getUniqueString()
        )
        self.SERVICE_GRAPH_NAME = 'my_service_graph' + self.getUniqueString()
        self.op_net_client = self.operator_cloud.network

        net = self.op_net_client.create_network(name=self.NET_NAME)
        self.assertIsInstance(net, _network.Network)
        self.NETWORK = net
        subnet = self.operator_cloud.network.create_subnet(
            name=self.SUBNET_NAME,
            ip_version=4,
            network_id=self.NETWORK.id,
            cidr=self.CIDR,
        )
        self.assertIsInstance(subnet, _subnet.Subnet)
        self.SUBNET = subnet

        self.PORT1 = self._create_port(
            network=self.NETWORK, port_name=self.PORT1_NAME
        )
        self.PORT2 = self._create_port(
            network=self.NETWORK, port_name=self.PORT2_NAME
        )

        flow_cls = self.op_net_client.create_sfc_flow_classifier(
            name=self.FLOW_CLASSIFIER_NAME,
            ethertype=self.ETHERTYPE,
            protocol=self.PROTOCOL,
            source_port_range_min=self.S_PORT_RANGE_MIN,
            source_port_range_max=self.S_PORT_RANGE_MAX,
            destination_port_range_min=self.D_PORT_RANGE_MIN,
            destination_port_range_max=self.D_PORT_RANGE_MAX,
            source_ip_prefix=self.SOURCE_IP,
            destination_ip_prefix=self.DESTINATION_IP,
            logical_source_port=self.PORT1.id,
            logical_destination_port=self.PORT2.id,
        )
        self.assertIsInstance(flow_cls, _flow_classifier.SfcFlowClassifier)
        self.FLOW_CLASSIFIER = flow_cls
        self.FC_ID = flow_cls.id

    def _create_port(self, network, port_name):
        port = self.op_net_client.create_port(
            name=port_name,
            network_id=network.id,
        )
        self.assertIsInstance(port, _port.Port)
        return port

    def tearDown(self):
        sot = self.operator_cloud.network.delete_sfc_flow_classifier(
            self.FLOW_CLASSIFIER.id, ignore_missing=True
        )
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_port(self.PORT1.id)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_port(self.PORT2.id)
        self.assertIsNone(sot)

        sot = self.operator_cloud.network.delete_subnet(self.SUBNET.id)
        self.assertIsNone(sot)
        sot = self.operator_cloud.network.delete_network(self.NETWORK.id)
        self.assertIsNone(sot)
        super().tearDown()

    def test_sfc_flow_classifier(self):
        sot = self.operator_cloud.network.find_sfc_flow_classifier(
            self.FLOW_CLASSIFIER.name
        )
        self.assertEqual(self.ETHERTYPE, sot.ethertype)
        self.assertEqual(self.SOURCE_IP, sot.source_ip_prefix)
        self.assertEqual(self.PROTOCOL, sot.protocol)

        classifiers = [
            fc.name
            for fc in self.operator_cloud.network.sfc_flow_classifiers()
        ]
        self.assertIn(self.FLOW_CLASSIFIER_NAME, classifiers)

        classifier = self.operator_cloud.network.get_sfc_flow_classifier(
            self.FC_ID
        )
        self.assertEqual(self.FLOW_CLASSIFIER_NAME, classifier.name)
        self.assertEqual(self.FC_ID, classifier.id)

        classifier = self.operator_cloud.network.update_sfc_flow_classifier(
            self.FC_ID, name=self.UPDATE_NAME
        )
        self.assertEqual(self.UPDATE_NAME, classifier.name)
