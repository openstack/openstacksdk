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

"""
test_zone
----------------------------------

Functional tests for zone methods.
"""

from testtools import content

from openstack.tests.functional import base


class TestZone(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.user_cloud.has_service('dns'):
            self.skipTest('dns service not supported by cloud')

    def test_zones(self):
        '''Test DNS zones functionality'''
        name = 'example.net.'
        zone_type = 'primary'
        email = 'test@example.net'
        description = 'Test zone'
        ttl = 3600
        masters = None

        self.addDetail('zone', content.text_content(name))
        self.addCleanup(self.cleanup, name)

        # Test we can create a zone and we get it returned
        zone = self.user_cloud.create_zone(
            name=name,
            zone_type=zone_type,
            email=email,
            description=description,
            ttl=ttl,
            masters=masters,
        )
        self.assertEqual(zone['name'], name)
        self.assertEqual(zone['type'], zone_type.upper())
        self.assertEqual(zone['email'], email)
        self.assertEqual(zone['description'], description)
        self.assertEqual(zone['ttl'], ttl)
        self.assertEqual(zone['masters'], [])

        # Test that we can list zones
        zones = self.user_cloud.list_zones()
        self.assertIsNotNone(zones)

        # Test we get the same zone with the get_zone method
        zone_get = self.user_cloud.get_zone(zone['id'])
        self.assertEqual(zone_get['id'], zone['id'])

        # Test the get method also works by name
        zone_get = self.user_cloud.get_zone(name)
        self.assertEqual(zone_get['name'], zone['name'])

        # Test we can update a field on the zone and only that field
        # is updated
        zone_update = self.user_cloud.update_zone(zone['id'], ttl=7200)
        self.assertEqual(zone_update['id'], zone['id'])
        self.assertEqual(zone_update['name'], zone['name'])
        self.assertEqual(zone_update['type'], zone['type'])
        self.assertEqual(zone_update['email'], zone['email'])
        self.assertEqual(zone_update['description'], zone['description'])
        self.assertEqual(zone_update['ttl'], 7200)
        self.assertEqual(zone_update['masters'], zone['masters'])

        # Test we can delete and get True returned
        zone_delete = self.user_cloud.delete_zone(zone['id'])
        self.assertTrue(zone_delete)

    def cleanup(self, name):
        self.user_cloud.delete_zone(name)
