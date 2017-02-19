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

from openstack.tests.functional import base


class TestServiceProvider(base.BaseFunctionalTest):
    def test_list(self):
        providers = list(self.conn.network.service_providers())
        names = [o.name for o in providers]
        service_types = [o.service_type for o in providers]
        self.assertIn('ha', names)
        self.assertIn('L3_ROUTER_NAT', service_types)
