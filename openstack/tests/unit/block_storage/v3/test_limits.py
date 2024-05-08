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

from openstack.block_storage.v3 import limits
from openstack.tests.unit import base

ABSOLUTE_LIMIT = {
    "totalSnapshotsUsed": 1,
    "maxTotalBackups": 10,
    "maxTotalVolumeGigabytes": 1000,
    "maxTotalSnapshots": 10,
    "maxTotalBackupGigabytes": 1000,
    "totalBackupGigabytesUsed": 1,
    "maxTotalVolumes": 10,
    "totalVolumesUsed": 2,
    "totalBackupsUsed": 3,
    "totalGigabytesUsed": 2,
}

RATE_LIMIT = {
    "verb": "POST",
    "value": 80,
    "remaining": 80,
    "unit": "MINUTE",
    "next-available": "2021-02-23T22:08:00Z",
}

RATE_LIMITS = {"regex": ".*", "uri": "*", "limit": [RATE_LIMIT]}

LIMIT = {"rate": [RATE_LIMITS], "absolute": ABSOLUTE_LIMIT}


class TestAbsoluteLimit(base.TestCase):
    def test_basic(self):
        limit_resource = limits.AbsoluteLimit()
        self.assertIsNone(limit_resource.resource_key)
        self.assertIsNone(limit_resource.resources_key)
        self.assertEqual('', limit_resource.base_path)
        self.assertFalse(limit_resource.allow_create)
        self.assertFalse(limit_resource.allow_fetch)
        self.assertFalse(limit_resource.allow_delete)
        self.assertFalse(limit_resource.allow_commit)
        self.assertFalse(limit_resource.allow_list)

    def test_make_absolute_limit(self):
        limit_resource = limits.AbsoluteLimit(**ABSOLUTE_LIMIT)
        self.assertEqual(
            ABSOLUTE_LIMIT['totalSnapshotsUsed'],
            limit_resource.total_snapshots_used,
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['maxTotalBackups'], limit_resource.max_total_backups
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['maxTotalVolumeGigabytes'],
            limit_resource.max_total_volume_gigabytes,
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['maxTotalSnapshots'],
            limit_resource.max_total_snapshots,
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['maxTotalBackupGigabytes'],
            limit_resource.max_total_backup_gigabytes,
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['totalBackupGigabytesUsed'],
            limit_resource.total_backup_gigabytes_used,
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['maxTotalVolumes'], limit_resource.max_total_volumes
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['totalVolumesUsed'],
            limit_resource.total_volumes_used,
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['totalBackupsUsed'],
            limit_resource.total_backups_used,
        )
        self.assertEqual(
            ABSOLUTE_LIMIT['totalGigabytesUsed'],
            limit_resource.total_gigabytes_used,
        )


class TestRateLimit(base.TestCase):
    def test_basic(self):
        limit_resource = limits.RateLimit()
        self.assertIsNone(limit_resource.resource_key)
        self.assertIsNone(limit_resource.resources_key)
        self.assertEqual('', limit_resource.base_path)
        self.assertFalse(limit_resource.allow_create)
        self.assertFalse(limit_resource.allow_fetch)
        self.assertFalse(limit_resource.allow_delete)
        self.assertFalse(limit_resource.allow_commit)
        self.assertFalse(limit_resource.allow_list)

    def test_make_rate_limit(self):
        limit_resource = limits.RateLimit(**RATE_LIMIT)
        self.assertEqual(RATE_LIMIT['verb'], limit_resource.verb)
        self.assertEqual(RATE_LIMIT['value'], limit_resource.value)
        self.assertEqual(RATE_LIMIT['remaining'], limit_resource.remaining)
        self.assertEqual(RATE_LIMIT['unit'], limit_resource.unit)
        self.assertEqual(
            RATE_LIMIT['next-available'], limit_resource.next_available
        )


class TestRateLimits(base.TestCase):
    def test_basic(self):
        limit_resource = limits.RateLimits()
        self.assertIsNone(limit_resource.resource_key)
        self.assertIsNone(limit_resource.resources_key)
        self.assertEqual('', limit_resource.base_path)
        self.assertFalse(limit_resource.allow_create)
        self.assertFalse(limit_resource.allow_fetch)
        self.assertFalse(limit_resource.allow_delete)
        self.assertFalse(limit_resource.allow_commit)
        self.assertFalse(limit_resource.allow_list)

    def _test_rate_limit(self, expected, actual):
        self.assertEqual(expected[0]['verb'], actual[0].verb)
        self.assertEqual(expected[0]['value'], actual[0].value)
        self.assertEqual(expected[0]['remaining'], actual[0].remaining)
        self.assertEqual(expected[0]['unit'], actual[0].unit)
        self.assertEqual(
            expected[0]['next-available'], actual[0].next_available
        )

    def test_make_rate_limits(self):
        limit_resource = limits.RateLimits(**RATE_LIMITS)
        self.assertEqual(RATE_LIMITS['regex'], limit_resource.regex)
        self.assertEqual(RATE_LIMITS['uri'], limit_resource.uri)
        self._test_rate_limit(RATE_LIMITS['limit'], limit_resource.limits)


class TestLimit(base.TestCase):
    def test_basic(self):
        limit_resource = limits.Limits()
        self.assertEqual('limits', limit_resource.resource_key)
        self.assertEqual('/limits', limit_resource.base_path)
        self.assertTrue(limit_resource.allow_fetch)
        self.assertFalse(limit_resource.allow_create)
        self.assertFalse(limit_resource.allow_commit)
        self.assertFalse(limit_resource.allow_delete)
        self.assertFalse(limit_resource.allow_list)

    def _test_absolute_limit(self, expected, actual):
        self.assertEqual(
            expected['totalSnapshotsUsed'], actual.total_snapshots_used
        )
        self.assertEqual(expected['maxTotalBackups'], actual.max_total_backups)
        self.assertEqual(
            expected['maxTotalVolumeGigabytes'],
            actual.max_total_volume_gigabytes,
        )
        self.assertEqual(
            expected['maxTotalSnapshots'], actual.max_total_snapshots
        )
        self.assertEqual(
            expected['maxTotalBackupGigabytes'],
            actual.max_total_backup_gigabytes,
        )
        self.assertEqual(
            expected['totalBackupGigabytesUsed'],
            actual.total_backup_gigabytes_used,
        )
        self.assertEqual(expected['maxTotalVolumes'], actual.max_total_volumes)
        self.assertEqual(
            expected['totalVolumesUsed'], actual.total_volumes_used
        )
        self.assertEqual(
            expected['totalBackupsUsed'], actual.total_backups_used
        )
        self.assertEqual(
            expected['totalGigabytesUsed'], actual.total_gigabytes_used
        )

    def _test_rate_limit(self, expected, actual):
        self.assertEqual(expected[0]['verb'], actual[0].verb)
        self.assertEqual(expected[0]['value'], actual[0].value)
        self.assertEqual(expected[0]['remaining'], actual[0].remaining)
        self.assertEqual(expected[0]['unit'], actual[0].unit)
        self.assertEqual(
            expected[0]['next-available'], actual[0].next_available
        )

    def _test_rate_limits(self, expected, actual):
        self.assertEqual(expected[0]['regex'], actual[0].regex)
        self.assertEqual(expected[0]['uri'], actual[0].uri)
        self._test_rate_limit(expected[0]['limit'], actual[0].limits)

    def test_make_limit(self):
        limit_resource = limits.Limits(**LIMIT)
        self._test_rate_limits(LIMIT['rate'], limit_resource.rate)
        self._test_absolute_limit(LIMIT['absolute'], limit_resource.absolute)
