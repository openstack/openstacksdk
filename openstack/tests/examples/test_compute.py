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

import unittest

from examples.compute import create
from examples.compute import delete
from examples.compute import find as compute_find
from examples.compute import list as compute_list
from examples import connect
from examples.network import find as network_find
from examples.network import list as network_list


class TestCompute(unittest.TestCase):
    """Test the compute examples

    The purpose of these tests is to ensure the examples run without erring
    out.
    """

    @classmethod
    def setUpClass(cls):
        cls.conn = connect.create_connection_from_config()

    def test_compute(self):
        compute_list.list_servers(self.conn)
        compute_list.list_images(self.conn)
        compute_list.list_flavors(self.conn)
        compute_list.list_keypairs(self.conn)
        network_list.list_networks(self.conn)

        compute_find.find_image(self.conn)
        compute_find.find_flavor(self.conn)
        compute_find.find_keypair(self.conn)
        network_find.find_network(self.conn)

        create.create_server(self.conn)

        delete.delete_keypair(self.conn)
        delete.delete_server(self.conn)
