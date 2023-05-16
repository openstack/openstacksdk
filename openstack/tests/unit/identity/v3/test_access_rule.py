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

from openstack.identity.v3 import access_rule
from openstack.tests.unit import base

EXAMPLE = {
    "links": {
        "self": "https://example.com/identity/v3/access_rules"
        "/07d719df00f349ef8de77d542edf010c"
    },
    "path": "/v2.1/servers/{server_id}/ips",
    "method": "GET",
    "service": "compute",
}


class TestAccessRule(base.TestCase):
    def test_basic(self):
        sot = access_rule.AccessRule()
        self.assertEqual('access_rule', sot.resource_key)
        self.assertEqual('access_rules', sot.resources_key)
        self.assertEqual('/users/%(user_id)s/access_rules', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = access_rule.AccessRule(**EXAMPLE)
        self.assertEqual(EXAMPLE['path'], sot.path)
        self.assertEqual(EXAMPLE['method'], sot.method)
        self.assertEqual(EXAMPLE['service'], sot.service)
        self.assertEqual(EXAMPLE['links'], sot.links)
