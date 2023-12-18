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

from openstack.dns.v2 import floating_ip as fip
from openstack.tests.unit import base


IDENTIFIER = 'RegionOne:id'
EXAMPLE = {
    'status': 'PENDING',
    'ptrdname': 'smtp.example.com.',
    'description': 'This is a floating ip for 127.0.0.1',
    'links': {'self': 'dummylink/reverse/floatingips/RegionOne:id'},
    'ttl': 600,
    'address': '172.24.4.10',
    'action': 'CREATE',
    'id': IDENTIFIER,
}


class TestFloatingIP(base.TestCase):
    def test_basic(self):
        sot = fip.FloatingIP()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('floatingips', sot.resources_key)
        self.assertEqual('/reverse/floatingips', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

        self.assertEqual('PATCH', sot.commit_method)

    def test_make_it(self):
        sot = fip.FloatingIP(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['ptrdname'], sot.ptrdname)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['ttl'], sot.ttl)
        self.assertEqual(EXAMPLE['address'], sot.address)
        self.assertEqual(EXAMPLE['action'], sot.action)
        self.assertEqual(EXAMPLE['status'], sot.status)
