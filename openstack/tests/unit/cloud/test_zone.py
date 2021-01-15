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

from openstack.tests.unit import base

from openstack import exceptions


zone_dict = {
    'name': 'example.net.',
    'type': 'PRIMARY',
    'email': 'test@example.net',
    'description': 'Example zone',
    'ttl': 3600,
    'id': '1'
}


class ZoneTestWrapper:

    def __init__(self, ut, attrs):
        self.remote_res = attrs
        self.ut = ut

    def get_create_response_json(self):
        return self.remote_res

    def get_get_response_json(self):
        return self.remote_res

    def __getitem__(self, key):
        """Dict access to be able to access properties easily
        """
        return self.remote_res[key]

    def cmp(self, other):
        ut = self.ut
        me = self.remote_res

        for k, v in me.items():
            # Go over known attributes. We might of course compare others,
            # but not necessary here
            ut.assertEqual(v, other[k])


class TestZone(base.TestCase):

    def setUp(self):
        super(TestZone, self).setUp()
        self.use_designate()

    def test_create_zone(self):
        fake_zone = ZoneTestWrapper(self, zone_dict)
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json=fake_zone.get_create_response_json(),
                 validate=dict(json={
                     'description': zone_dict['description'],
                     'email': zone_dict['email'],
                     'name': zone_dict['name'],
                     'ttl': zone_dict['ttl'],
                     'type': 'PRIMARY'
                 }))
        ])
        z = self.cloud.create_zone(
            name=zone_dict['name'],
            zone_type=zone_dict['type'],
            email=zone_dict['email'],
            description=zone_dict['description'],
            ttl=zone_dict['ttl'],
            masters=None)
        fake_zone.cmp(z)
        self.assert_calls()

    def test_create_zone_exception(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 status_code=500)
        ])

        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_zone,
            'example.net.'
        )
        self.assert_calls()

    def test_update_zone(self):
        fake_zone = ZoneTestWrapper(self, zone_dict)
        new_ttl = 7200
        updated_zone_dict = copy.copy(zone_dict)
        updated_zone_dict['ttl'] = new_ttl
        updated_zone = ZoneTestWrapper(self, updated_zone_dict)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 json=fake_zone.get_get_response_json()),
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 json=updated_zone.get_get_response_json(),
                 validate=dict(json={"ttl": new_ttl}))
        ])
        z = self.cloud.update_zone(fake_zone['id'], ttl=new_ttl)
        updated_zone.cmp(z)
        self.assert_calls()

    def test_delete_zone(self):
        fake_zone = ZoneTestWrapper(self, zone_dict)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 json=fake_zone.get_get_response_json()),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 status_code=202)
        ])
        self.assertTrue(self.cloud.delete_zone(fake_zone['id']))
        self.assert_calls()

    def test_get_zone_by_id(self):
        fake_zone = ZoneTestWrapper(self, zone_dict)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 json=fake_zone.get_get_response_json())
        ])
        res = self.cloud.get_zone(fake_zone['id'])

        fake_zone.cmp(res)
        self.assert_calls()

    def test_get_zone_by_name(self):
        fake_zone = ZoneTestWrapper(self, zone_dict)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['name']]),
                 status_code=404),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones'],
                     qs_elements=[
                        'name={name}'.format(name=fake_zone['name'])]),
                 json={"zones": [fake_zone.get_get_response_json()]})
        ])
        res = self.cloud.get_zone(fake_zone['name'])
        fake_zone.cmp(res)
        self.assert_calls()

    def test_get_zone_not_found_returns_false(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', 'nonexistingzone.net.']),
                 status_code=404),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones'],
                     qs_elements=['name=nonexistingzone.net.']),
                 json={"zones": []})
        ])
        zone = self.cloud.get_zone('nonexistingzone.net.')
        self.assertFalse(zone)
        self.assert_calls()

    def test_list_zones(self):
        fake_zone = ZoneTestWrapper(self, zone_dict)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones']),
                 json={'zones': [fake_zone.get_get_response_json()],
                       'links': {
                           'next': self.get_mock_url(
                               'dns', 'public',
                               append=['v2', 'zones/'],
                               qs_elements=['limit=1', 'marker=asd']),
                           'self': self.get_mock_url(
                               'dns', 'public',
                               append=['v2', 'zones/'],
                               qs_elements=['limit=1'])},
                       'metadata':{'total_count': 2}}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones/'],
                     qs_elements=[
                        'limit=1', 'marker=asd']),
                 json={'zones': [fake_zone.get_get_response_json()]}),
        ])
        res = self.cloud.list_zones()

        # updated_rs.cmp(res)
        self.assertEqual(2, len(res))
        self.assert_calls()
