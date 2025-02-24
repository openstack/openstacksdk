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


from openstack.dns.v2 import zone_nameserver
from openstack.tests.unit import base


class TestZoneNameserver(base.TestCase):
    def test_basic(self):
        sot = zone_nameserver.ZoneNameserver()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('nameservers', sot.resources_key)
        self.assertEqual('/zones/%(zone_id)s/nameservers', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_commit)

        self.assertDictEqual({}, sot._query_mapping._mapping)

    def test_make_it(self):
        hostname = 'bogus-hostname'
        priority = 123

        sot = zone_nameserver.ZoneNameserver(
            hostname=hostname, priority=priority
        )
        self.assertEqual(hostname, sot.hostname)
        self.assertEqual(priority, sot.priority)
