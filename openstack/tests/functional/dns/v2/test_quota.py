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


class TestQuota(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.require_service("dns")
        if not self._operator_cloud_name:
            self.skip("Operator cloud must be set for this test")

        self.project = self.create_temporary_project()

    def test_quota(self):
        # set quota

        attrs = {
            "api_export_size": 1,
            "recordset_records": 2,
            "zone_records": 3,
            "zone_recordsets": 4,
            "zones": 5,
        }
        new_quota = self.operator_cloud.dns.update_quota(
            self.project.id, **attrs
        )
        self.assertEqual(attrs["api_export_size"], new_quota.api_export_size)
        self.assertEqual(
            attrs["recordset_records"], new_quota.recordset_records
        )
        self.assertEqual(attrs["zone_records"], new_quota.zone_records)
        self.assertEqual(attrs["zone_recordsets"], new_quota.zone_recordsets)
        self.assertEqual(attrs["zones"], new_quota.zones)

        # get quota

        expected_keys = [
            "id",
            "api_export_size",
            "recordset_records",
            "zone_records",
            "zone_recordsets",
            "zones",
        ]
        test_quota = self.operator_cloud.dns.get_quota(self.project.id)
        for actual_key in test_quota._body.attributes.keys():
            self.assertIn(actual_key, expected_keys)
        self.assertEqual(self.project.id, test_quota.id)
        self.assertEqual(attrs["api_export_size"], test_quota.api_export_size)
        self.assertEqual(
            attrs["recordset_records"], test_quota.recordset_records
        )
        self.assertEqual(attrs["zone_records"], test_quota.zone_records)
        self.assertEqual(attrs["zone_recordsets"], test_quota.zone_recordsets)
        self.assertEqual(attrs["zones"], test_quota.zones)

        # reset quota

        self.operator_cloud.dns.delete_quota(self.project.id)
