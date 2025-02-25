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

from examples.network import create as network_create
from examples.network import delete as network_delete
from examples.network import find as network_find
from examples.network import list as network_list

from openstack.tests.functional import base


class TestNetwork(base.BaseFunctionalTest):
    """Test the network examples

    The purpose of these tests is to ensure the examples run successfully.
    """

    def test_network(self):
        network_list.list_networks(self.operator_cloud)
        network_list.list_subnets(self.operator_cloud)
        network_list.list_ports(self.operator_cloud)
        network_list.list_security_groups(self.operator_cloud)
        network_list.list_routers(self.operator_cloud)

        network_find.find_network(self.operator_cloud)

        network_create.create_network(self.operator_cloud)
        network_delete.delete_network(self.operator_cloud)
