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

from openstack.dns.v2 import limit as _limit
from openstack.tests.unit import base

IDENTIFIER = 'limit'
EXAMPLE = {
    "max_page_limit": 1000,
    "max_recordset_name_length": 255,
    "max_recordset_records": 20,
    "max_zone_name_length": 255,
    "max_zone_records": 500,
    "max_zone_recordsets": 500,
    "max_zones": 10,
    "min_ttl": 100,
}


class TestLimit(base.TestCase):
    def test_basic(self):
        sot = _limit.Limit()
        self.assertEqual('limit', sot.resource_key)
        self.assertEqual(None, sot.resources_key)
        self.assertEqual('/limits', sot.base_path)
        self.assertTrue(sot.allow_list)
