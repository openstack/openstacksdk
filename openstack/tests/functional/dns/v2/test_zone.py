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

from openstack import connection
from openstack.tests.functional import base


class TestZone(base.BaseFunctionalTest):

    def setUp(self):
        super(TestZone, self).setUp()
        self.require_service('dns')

        self.conn = connection.from_config(cloud_name=base.TEST_CLOUD_NAME)

        # Note: zone deletion is not an immediate operation, so each time
        # chose a new zone name for a test
        # getUniqueString is not guaranteed to return unique string between
        # different tests of the same class.
        self.ZONE_NAME = 'example-{0}.org.'.format(random.randint(1, 10000))

        self.zone = self.conn.dns.create_zone(
            name=self.ZONE_NAME,
            email='joe@example.org',
            type='PRIMARY',
            ttl=7200,
            description='example zone'
        )
        self.addCleanup(self.conn.dns.delete_zone, self.zone)

    def test_get_zone(self):
        zone = self.conn.dns.get_zone(self.zone)
        self.assertEqual(self.zone, zone)

    def test_list_zones(self):
        names = [f.name for f in self.conn.dns.zones()]
        self.assertIn(self.ZONE_NAME, names)

    def test_create_rs(self):
        zone = self.conn.dns.get_zone(self.zone)
        self.assertIsNotNone(self.conn.dns.create_recordset(
            zone=zone,
            name='www.{zone}'.format(zone=zone.name),
            type='A',
            description='Example zone rec',
            ttl=3600,
            records=['192.168.1.1']
        ))
