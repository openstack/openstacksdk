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

import testtools

from openstack.network.v2 import quota

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'floatingip': 1,
    'network': 2,
    'port': 3,
    'tenant_id': '4',
    'router': 5,
    'subnet': 6,
}


class TestQuota(testtools.TestCase):

    def test_basic(self):
        sot = quota.Quota()
        self.assertEqual('quota', sot.resource_key)
        self.assertEqual('quotas', sot.resources_key)
        self.assertEqual('/quotas', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = quota.Quota(EXAMPLE)
        self.assertEqual(EXAMPLE['floatingip'], sot.floating_ip)
        self.assertEqual(EXAMPLE['network'], sot.network)
        self.assertEqual(EXAMPLE['port'], sot.port)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['router'], sot.router)
        self.assertEqual(EXAMPLE['subnet'], sot.subnet)
