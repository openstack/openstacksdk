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

import copy
import testtools

import openstack.cloud
from openstack.tests.unit import base


zone_dict = {
    'name': 'example.net.',
    'type': 'PRIMARY',
    'email': 'test@example.net',
    'description': 'Example zone',
    'ttl': 3600,
}

new_zone_dict = copy.copy(zone_dict)
new_zone_dict['id'] = '1'


class TestZone(base.TestCase):

    def setUp(self):
        super(TestZone, self).setUp()
        self.use_designate()

    def test_create_zone(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json=new_zone_dict,
                 validate=dict(
                     json=zone_dict))
        ])
        z = self.cloud.create_zone(
            name=zone_dict['name'],
            zone_type=zone_dict['type'],
            email=zone_dict['email'],
            description=zone_dict['description'],
            ttl=zone_dict['ttl'],
            masters=None)
        self.assertEqual(new_zone_dict, z)
        self.assert_calls()

    def test_create_zone_exception(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 status_code=500)
        ])
        with testtools.ExpectedException(
            openstack.cloud.exc.OpenStackCloudHTTPError,
            "Unable to create zone example.net."
        ):
            self.cloud.create_zone('example.net.')
        self.assert_calls()

    def test_update_zone(self):
        new_ttl = 7200
        updated_zone = copy.copy(new_zone_dict)
        updated_zone['ttl'] = new_ttl
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [new_zone_dict],
                     "links": {},
                     "metadata": {
                         'total_count': 1}}),
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', '1']),
                 json=updated_zone,
                 validate=dict(
                     json={"ttl": new_ttl}))
        ])
        z = self.cloud.update_zone('1', ttl=new_ttl)
        self.assertEqual(updated_zone, z)
        self.assert_calls()

    def test_delete_zone(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [new_zone_dict],
                     "links": {},
                     "metadata": {
                         'total_count': 1}}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', '1']),
                 json=new_zone_dict)
        ])
        self.assertTrue(self.cloud.delete_zone('1'))
        self.assert_calls()

    def test_get_zone_by_id(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [new_zone_dict],
                     "links": {},
                     "metadata": {
                         'total_count': 1}})
        ])
        zone = self.cloud.get_zone('1')
        self.assertEqual(zone['id'], '1')
        self.assert_calls()

    def test_get_zone_by_name(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [new_zone_dict],
                     "links": {},
                     "metadata": {
                         'total_count': 1}})
        ])
        zone = self.cloud.get_zone('example.net.')
        self.assertEqual(zone['name'], 'example.net.')
        self.assert_calls()

    def test_get_zone_not_found_returns_false(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [],
                     "links": {},
                     "metadata": {
                         'total_count': 1}})
        ])
        zone = self.cloud.get_zone('nonexistingzone.net.')
        self.assertFalse(zone)
        self.assert_calls()
