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

import uuid

from openstack import exceptions
from openstack.tests.functional import base
from openstack import utils


class TestZoneShare(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('dns')
        if not self.user_cloud:
            self.skipTest("The demo cloud is required for this test")

        # Note: zone deletion is not an immediate operation, so each time
        # chose a new zone name for a test
        # getUniqueString is not guaranteed to return unique string between
        # different tests of the same class.
        self.ZONE_NAME = f'example-{uuid.uuid4().hex}.org.'

        # Make sure the API under test has shared zones support
        if not utils.supports_version(self.operator_cloud.dns, '2.1'):
            self.skipTest(
                'Designate API version does not support shared zones.'
            )

        self.zone = self.operator_cloud.dns.create_zone(
            name=self.ZONE_NAME,
            email='joe@example.org',
            type='PRIMARY',
            ttl=7200,
            description='example zone for sdk zone share tests',
        )
        self.addCleanup(
            self.operator_cloud.dns.delete_zone,
            self.zone,
            delete_shares=True,
        )

        self.project_id = self.operator_cloud.session.get_project_id()
        self.demo_project_id = self.user_cloud.session.get_project_id()

    def test_create_delete_zone_share(self):
        zone_share = self.operator_cloud.dns.create_zone_share(
            self.zone, target_project_id=self.demo_project_id
        )
        self.addCleanup(
            self.operator_cloud.dns.delete_zone_share,
            self.zone,
            zone_share,
        )

        self.assertEqual(self.zone.id, zone_share.zone_id)
        self.assertEqual(self.project_id, zone_share.project_id)
        self.assertEqual(self.demo_project_id, zone_share.target_project_id)
        self.assertIsNotNone(zone_share.id)
        self.assertIsNotNone(zone_share.created_at)
        self.assertIsNone(zone_share.updated_at)

    def test_get_zone_share(self):
        orig_zone_share = self.operator_cloud.dns.create_zone_share(
            self.zone,
            target_project_id=self.demo_project_id,
        )
        self.addCleanup(
            self.operator_cloud.dns.delete_zone_share,
            self.zone,
            orig_zone_share,
        )

        zone_share = self.operator_cloud.dns.get_zone_share(
            self.zone,
            orig_zone_share,
        )

        self.assertEqual(self.zone.id, zone_share.zone_id)
        self.assertEqual(self.project_id, zone_share.project_id)
        self.assertEqual(self.demo_project_id, zone_share.target_project_id)
        self.assertEqual(orig_zone_share.id, zone_share.id)
        self.assertEqual(orig_zone_share.created_at, zone_share.created_at)
        self.assertEqual(orig_zone_share.updated_at, zone_share.updated_at)

    def test_find_zone_share(self):
        orig_zone_share = self.operator_cloud.dns.create_zone_share(
            self.zone, target_project_id=self.demo_project_id
        )
        self.addCleanup(
            self.operator_cloud.dns.delete_zone_share,
            self.zone,
            orig_zone_share,
        )

        zone_share = self.operator_cloud.dns.find_zone_share(
            self.zone,
            orig_zone_share.id,
        )

        self.assertEqual(self.zone.id, zone_share.zone_id)
        self.assertEqual(self.project_id, zone_share.project_id)
        self.assertEqual(self.demo_project_id, zone_share.target_project_id)
        self.assertEqual(orig_zone_share.id, zone_share.id)
        self.assertEqual(orig_zone_share.created_at, zone_share.created_at)
        self.assertEqual(orig_zone_share.updated_at, zone_share.updated_at)

    def test_find_zone_share_ignore_missing(self):
        zone_share = self.operator_cloud.dns.find_zone_share(
            self.zone,
            'bogus_id',
        )
        self.assertIsNone(zone_share)

    def test_find_zone_share_ignore_missing_false(self):
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.dns.find_zone_share,
            self.zone,
            'bogus_id',
            ignore_missing=False,
        )

    def test_list_zone_shares(self):
        zone_share = self.operator_cloud.dns.create_zone_share(
            self.zone,
            target_project_id=self.demo_project_id,
        )
        self.addCleanup(
            self.operator_cloud.dns.delete_zone_share,
            self.zone,
            zone_share,
        )

        target_ids = [
            o.target_project_id
            for o in self.operator_cloud.dns.zone_shares(self.zone)
        ]
        self.assertIn(self.demo_project_id, target_ids)

    def test_list_zone_shares_with_target_id(self):
        zone_share = self.operator_cloud.dns.create_zone_share(
            self.zone,
            target_project_id=self.demo_project_id,
        )
        self.addCleanup(
            self.operator_cloud.dns.delete_zone_share,
            self.zone,
            zone_share,
        )

        target_ids = [
            o.target_project_id
            for o in self.operator_cloud.dns.zone_shares(
                self.zone, target_project_id=self.demo_project_id
            )
        ]
        self.assertIn(self.demo_project_id, target_ids)
