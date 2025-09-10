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

from openstack.dns.v2 import quota
from openstack.tests.unit import base

IDENTIFIER = "IDENTIFIER"
EXAMPLE = {
    "zones": 10,
    "zone_recordsets": 500,
    "zone_records": 500,
    "recordset_records": 20,
    "api_export_size": 1000,
}


class TestQuota(base.TestCase):
    def test_basic(self):
        sot = quota.Quota()
        self.assertIsNone(sot.resources_key)
        self.assertIsNone(sot.resource_key)
        self.assertEqual("/quotas", sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.commit_method, "PATCH")

    def test_make_it(self):
        sot = quota.Quota(project='FAKE_PROJECT', **EXAMPLE)
        self.assertEqual(EXAMPLE['zones'], sot.zones)
        self.assertEqual(EXAMPLE['zone_recordsets'], sot.zone_recordsets)
        self.assertEqual(EXAMPLE['zone_records'], sot.zone_records)
        self.assertEqual(EXAMPLE['recordset_records'], sot.recordset_records)
        self.assertEqual(EXAMPLE['api_export_size'], sot.api_export_size)
        self.assertEqual('FAKE_PROJECT', sot.project)

    def test_prepare_request(self):
        body = {'id': 'ABCDEFGH', 'zones': 20}
        quota_obj = quota.Quota(**body)
        response = quota_obj._prepare_request()
        self.assertNotIn('id', response)
