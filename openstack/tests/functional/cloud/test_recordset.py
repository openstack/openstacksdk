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
test_recordset
----------------------------------

Functional tests for recordset methods.
"""

import random
import string

from testtools import content

from openstack.tests.functional import base


class TestRecordset(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.user_cloud.has_service('dns'):
            self.skipTest('dns service not supported by cloud')

    def test_recordsets_with_zone_id(self):
        '''Test DNS recordsets functionality'''
        sub = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))

        zone = f'{sub}.example2.net.'
        email = 'test@example2.net'
        name = f'www.{zone}'
        type_ = 'a'
        description = 'Test recordset'
        ttl = 3600
        records = ['192.168.1.1']

        self.addDetail('zone', content.text_content(zone))
        self.addDetail('recordset', content.text_content(name))

        # Create a zone to hold the tested recordset
        zone_obj = self.user_cloud.create_zone(name=zone, email=email)

        # Test we can create a recordset and we get it returned
        created_recordset = self.user_cloud.create_recordset(
            zone_obj['id'], name, type_, records, description, ttl
        )
        self.addCleanup(self.cleanup, zone, created_recordset['id'])

        self.assertEqual(created_recordset['zone_id'], zone_obj['id'])
        self.assertEqual(created_recordset['name'], name)
        self.assertEqual(created_recordset['type'], type_.upper())
        self.assertEqual(created_recordset['records'], records)
        self.assertEqual(created_recordset['description'], description)
        self.assertEqual(created_recordset['ttl'], ttl)

        # Test that we can list recordsets
        recordsets = self.user_cloud.list_recordsets(
            zone_obj['id'],
        )
        self.assertIsNotNone(recordsets)

        # Test we get the same recordset with the get_recordset method
        get_recordset = self.user_cloud.get_recordset(
            zone_obj['id'], created_recordset['id']
        )
        self.assertEqual(get_recordset['id'], created_recordset['id'])

        # Test we can update a field on the recordset and only that field
        # is updated
        updated_recordset = self.user_cloud.update_recordset(
            zone_obj['id'], created_recordset['id'], ttl=7200
        )
        self.assertEqual(updated_recordset['id'], created_recordset['id'])
        self.assertEqual(updated_recordset['name'], name)
        self.assertEqual(updated_recordset['type'], type_.upper())
        self.assertEqual(updated_recordset['records'], records)
        self.assertEqual(updated_recordset['description'], description)
        self.assertEqual(updated_recordset['ttl'], 7200)

        # Test we can delete and get True returned
        deleted_recordset = self.user_cloud.delete_recordset(
            zone, created_recordset['id']
        )
        self.assertTrue(deleted_recordset)

    def test_recordsets_with_zone_name(self):
        '''Test DNS recordsets functionality'''
        sub = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))

        zone = f'{sub}.example2.net.'
        email = 'test@example2.net'
        name = f'www.{zone}'
        type_ = 'a'
        description = 'Test recordset'
        ttl = 3600
        records = ['192.168.1.1']

        self.addDetail('zone', content.text_content(zone))
        self.addDetail('recordset', content.text_content(name))

        # Create a zone to hold the tested recordset
        zone_obj = self.user_cloud.create_zone(name=zone, email=email)

        # Test we can create a recordset and we get it returned
        created_recordset = self.user_cloud.create_recordset(
            zone, name, type_, records, description, ttl
        )
        self.addCleanup(self.cleanup, zone, created_recordset['id'])

        self.assertEqual(created_recordset['zone_id'], zone_obj['id'])
        self.assertEqual(created_recordset['name'], name)
        self.assertEqual(created_recordset['type'], type_.upper())
        self.assertEqual(created_recordset['records'], records)
        self.assertEqual(created_recordset['description'], description)
        self.assertEqual(created_recordset['ttl'], ttl)

        # Test that we can list recordsets
        recordsets = self.user_cloud.list_recordsets(zone)
        self.assertIsNotNone(recordsets)

        # Test we get the same recordset with the get_recordset method
        get_recordset = self.user_cloud.get_recordset(
            zone, created_recordset['id']
        )
        self.assertEqual(get_recordset['id'], created_recordset['id'])

        # Test we can update a field on the recordset and only that field
        # is updated
        updated_recordset = self.user_cloud.update_recordset(
            zone_obj['id'], created_recordset['id'], ttl=7200
        )
        self.assertEqual(updated_recordset['id'], created_recordset['id'])
        self.assertEqual(updated_recordset['name'], name)
        self.assertEqual(updated_recordset['type'], type_.upper())
        self.assertEqual(updated_recordset['records'], records)
        self.assertEqual(updated_recordset['description'], description)
        self.assertEqual(updated_recordset['ttl'], 7200)

        # Test we can delete and get True returned
        deleted_recordset = self.user_cloud.delete_recordset(
            zone, created_recordset['id']
        )
        self.assertTrue(deleted_recordset)

    def cleanup(self, zone_name, recordset_id):
        self.user_cloud.delete_recordset(zone_name, recordset_id)
        self.user_cloud.delete_zone(zone_name)
