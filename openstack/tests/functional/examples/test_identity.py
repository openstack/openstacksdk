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

from examples.identity import list as identity_list

from openstack.tests.functional import base


class TestIdentity(base.BaseFunctionalTest):
    """Test the identity examples

    The purpose of these tests is to ensure the examples run successfully.
    """

    def test_identity(self):
        identity_list.list_users(self.operator_cloud)
        identity_list.list_credentials(self.operator_cloud)
        identity_list.list_projects(self.operator_cloud)
        identity_list.list_domains(self.operator_cloud)
        identity_list.list_groups(self.operator_cloud)
        identity_list.list_services(self.operator_cloud)
        identity_list.list_endpoints(self.operator_cloud)
        identity_list.list_regions(self.operator_cloud)
