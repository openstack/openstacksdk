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
import random

from openstack import exceptions
from openstack.tests.functional import base
from openstack import utils


class TestZone(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('dns')

        # Note: zone deletion is not an immediate operation, so each time
        # chose a new zone name for a test
        # getUniqueString is not guaranteed to return unique string between
        # different tests of the same class.
        self.ZONE_NAME = f'example-{random.randint(1, 10000)}.org.'

        self.zone = self.operator_cloud.dns.create_zone(
            name=self.ZONE_NAME,
            email='joe@example.org',
            type='PRIMARY',
            ttl=7200,
            description='example zone',
        )
        self.addCleanup(self.operator_cloud.dns.delete_zone, self.zone)

    def test_get_zone(self):
        zone = self.operator_cloud.dns.get_zone(self.zone)
        self.assertEqual(self.zone, zone)

    def test_list_zones(self):
        names = [f.name for f in self.operator_cloud.dns.zones()]
        self.assertIn(self.ZONE_NAME, names)

    def test_update_zone(self):
        current_ttl = self.operator_cloud.dns.get_zone(self.zone)['ttl']
        self.operator_cloud.dns.update_zone(self.zone, ttl=current_ttl + 1)
        updated_zone_ttl = self.operator_cloud.dns.get_zone(self.zone)['ttl']
        self.assertEqual(
            current_ttl + 1,
            updated_zone_ttl,
            f'Failed, updated TTL value is:{updated_zone_ttl} instead of expected:{current_ttl + 1}',
        )

    def test_create_rs(self):
        zone = self.operator_cloud.dns.get_zone(self.zone)
        self.assertIsNotNone(
            self.operator_cloud.dns.create_recordset(
                zone=zone,
                name=f'www.{zone.name}',
                type='A',
                description='Example zone rec',
                ttl=3600,
                records=['192.168.1.1'],
            )
        )

    def test_delete_zone_with_shares(self):
        # Make sure the API under test has shared zones support
        if not utils.supports_version(self.operator_cloud.dns, '2.1'):
            self.skipTest(
                'Designate API version does not support shared zones.'
            )

        zone_name = f'example-{random.randint(1, 10000)}.org.'
        zone = self.operator_cloud.dns.create_zone(
            name=zone_name,
            email='joe@example.org',
            type='PRIMARY',
            ttl=7200,
            description='example zone',
        )
        self.addCleanup(self.operator_cloud.dns.delete_zone, zone)

        demo_project_id = self.operator_cloud.get_project('demo')['id']
        zone_share = self.operator_cloud.dns.create_zone_share(
            zone, target_project_id=demo_project_id
        )
        self.addCleanup(
            self.operator_cloud.dns.delete_zone_share, zone, zone_share
        )

        # Test that we cannot delete a zone with shares
        self.assertRaises(
            exceptions.BadRequestException,
            self.operator_cloud.dns.delete_zone,
            zone,
        )

        self.operator_cloud.dns.delete_zone(zone, delete_shares=True)
