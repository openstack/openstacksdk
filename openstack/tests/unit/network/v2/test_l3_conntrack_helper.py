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

from openstack.network.v2 import l3_conntrack_helper
from openstack.tests.unit import base


EXAMPLE = {
    'id': 'ct_helper_id',
    'protocol': 'udp',
    'port': 69,
    'helper': 'tftp',
}


class TestL3ConntrackHelper(base.TestCase):
    def test_basic(self):
        sot = l3_conntrack_helper.ConntrackHelper()
        self.assertEqual('conntrack_helper', sot.resource_key)
        self.assertEqual('conntrack_helpers', sot.resources_key)
        self.assertEqual(
            '/routers/%(router_id)s/conntrack_helpers', sot.base_path
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = l3_conntrack_helper.ConntrackHelper(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['protocol'], sot.protocol)
        self.assertEqual(EXAMPLE['port'], sot.port)
        self.assertEqual(EXAMPLE['helper'], sot.helper)
