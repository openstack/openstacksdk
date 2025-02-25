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

from examples.compute import create
from examples.compute import delete
from examples.compute import find as compute_find
from examples.compute import list as compute_list
from examples.network import find as network_find
from examples.network import list as network_list

from openstack.tests.functional import base


class TestCompute(base.BaseFunctionalTest):
    """Test the compute examples

    The purpose of these tests is to ensure the examples run successfully.
    """

    def test_compute(self):
        compute_list.list_servers(self.operator_cloud)
        compute_list.list_images(self.operator_cloud)
        compute_list.list_flavors(self.operator_cloud)
        compute_list.list_keypairs(self.operator_cloud)
        network_list.list_networks(self.operator_cloud)

        compute_find.find_image(self.operator_cloud)
        compute_find.find_flavor(self.operator_cloud)
        compute_find.find_keypair(self.operator_cloud)
        network_find.find_network(self.operator_cloud)

        create.create_server(self.operator_cloud)

        delete.delete_keypair(self.operator_cloud)
        delete.delete_server(self.operator_cloud)
