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

from examples import connect
from examples.identity import list as identity_list


class TestIdentity(unittest.TestCase):
    """Test the identity examples

    The purpose of these tests is to ensure the examples run without erring
    out.
    """

    @classmethod
    def setUpClass(cls):
        cls.conn = connect.create_connection_from_config()

    def test_identity(self):
        identity_list.list_users(self.conn)
        identity_list.list_credentials(self.conn)
        identity_list.list_projects(self.conn)
        identity_list.list_domains(self.conn)
        identity_list.list_groups(self.conn)
        identity_list.list_services(self.conn)
        identity_list.list_endpoints(self.conn)
        identity_list.list_regions(self.conn)
