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

Functional tests for `shade` recordset methods.
"""

from testtools import content

from openstack.tests.functional.cloud import base


class TestRecordset(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestRecordset, self).setUp()
        if not self.user_cloud.has_service('dns'):
            self.skipTest('dns service not supported by cloud')

    def test_recordsets(self):
        '''Test DNS recordsets functionality'''
        zone = 'example2.net.'
        email = 'test@example2.net'
        name = 'www'
        type_ = 'a'
        description = 'Test recordset'
        ttl = 3600
        records = ['192.168.1.1']

        self.addDetail('zone', content.text_content(zone))
        self.addDetail('recordset', content.text_content(name))
        self.addCleanup(self.cleanup, zone, name)

        # Create a zone to hold the tested recordset
        zone_obj = self.user_cloud.create_zone(name=zone, email=email)

        # Test we can create a recordset and we get it returned
        created_recordset = self.user_cloud.create_recordset(zone, name, type_,
                                                             records,
                                                             description, ttl)
        self.assertEqual(created_recordset['zone_id'], zone_obj['id'])
        self.assertEqual(created_recordset['name'], name + '.' + zone)
        self.assertEqual(created_recordset['type'], type_.upper())
        self.assertEqual(created_recordset['records'], records)
        self.assertEqual(created_recordset['description'], description)
        self.assertEqual(created_recordset['ttl'], ttl)

        # Test that we can list recordsets
        recordsets = self.user_cloud.list_recordsets(zone)
        self.assertIsNotNone(recordsets)

        # Test we get the same recordset with the get_recordset method
        get_recordset = self.user_cloud.get_recordset(zone,
                                                      created_recordset['id'])
        self.assertEqual(get_recordset['id'], created_recordset['id'])

        # Test the get method also works by name
        get_recordset = self.user_cloud.get_recordset(zone, name + '.' + zone)
        self.assertEqual(get_recordset['id'], created_recordset['id'])

        # Test we can update a field on the recordset and only that field
        # is updated
        updated_recordset = self.user_cloud.update_recordset(zone_obj['id'],
                                                             name + '.' + zone,
                                                             ttl=7200)
        self.assertEqual(updated_recordset['id'], created_recordset['id'])
        self.assertEqual(updated_recordset['name'], name + '.' + zone)
        self.assertEqual(updated_recordset['type'], type_.upper())
        self.assertEqual(updated_recordset['records'], records)
        self.assertEqual(updated_recordset['description'], description)
        self.assertEqual(updated_recordset['ttl'], 7200)

        # Test we can delete and get True returned
        deleted_recordset = self.user_cloud.delete_recordset(
            zone, name + '.' + zone)
        self.assertTrue(deleted_recordset)

    def cleanup(self, zone_name, recordset_name):
        self.user_cloud.delete_recordset(
            zone_name, recordset_name + '.' + zone_name)
        self.user_cloud.delete_zone(zone_name)
