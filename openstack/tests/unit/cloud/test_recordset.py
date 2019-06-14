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
from openstack import exceptions
from openstack.tests.unit import base

from openstack.tests.unit.cloud import test_zone


zone = test_zone.zone_dict

recordset = {
    'name': 'www.example.net.',
    'type': 'A',
    'description': 'Example zone rec',
    'ttl': 3600,
    'records': ['192.168.1.1'],
    'id': '1',
    'zone_id': zone['id'],
    'zone_name': zone['name']
}


class RecordsetTestWrapper(test_zone.ZoneTestWrapper):
    pass


class TestRecordset(base.TestCase):

    def setUp(self):
        super(TestRecordset, self).setUp()
        self.use_designate()

    def test_create_recordset_zoneid(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        fake_rs = RecordsetTestWrapper(self, recordset)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 json=fake_zone.get_get_response_json()),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', zone['id'], 'recordsets']),
                 json=fake_rs.get_create_response_json(),
                 validate=dict(json={
                     "records": fake_rs['records'],
                     "type": fake_rs['type'],
                     "name": fake_rs['name'],
                     "description": fake_rs['description'],
                     "ttl": fake_rs['ttl']
                 })),
        ])
        rs = self.cloud.create_recordset(
            zone=fake_zone['id'],
            name=fake_rs['name'],
            recordset_type=fake_rs['type'],
            records=fake_rs['records'],
            description=fake_rs['description'],
            ttl=fake_rs['ttl'])

        fake_rs.cmp(rs)
        self.assert_calls()

    def test_create_recordset_zonename(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        fake_rs = RecordsetTestWrapper(self, recordset)
        self.register_uris([
            # try by directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones'],
                     qs_elements=[
                         'name={name}'.format(name=fake_zone['name'])]),
                     json={'zones': [fake_zone.get_get_response_json()]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', zone['id'], 'recordsets']),
                 json=fake_rs.get_create_response_json(),
                 validate=dict(json={
                     "records": fake_rs['records'],
                     "type": fake_rs['type'],
                     "name": fake_rs['name'],
                     "description": fake_rs['description'],
                     "ttl": fake_rs['ttl']
                 })),
        ])
        rs = self.cloud.create_recordset(
            zone=fake_zone['name'],
            name=fake_rs['name'],
            recordset_type=fake_rs['type'],
            records=fake_rs['records'],
            description=fake_rs['description'],
            ttl=fake_rs['ttl'])

        fake_rs.cmp(rs)
        self.assert_calls()

    def test_create_recordset_exception(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 json=fake_zone.get_get_response_json()),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', zone['id'], 'recordsets']),
                 status_code=500,
                 validate=dict(json={
                     'name': 'www2.example.net.',
                     'records': ['192.168.1.2'],
                     'type': 'A'})),
        ])

        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_recordset,
            fake_zone['id'], 'www2.example.net.', 'a', ['192.168.1.2']
        )

        self.assert_calls()

    def test_update_recordset(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        fake_rs = RecordsetTestWrapper(self, recordset)
        new_ttl = 7200
        expected_recordset = recordset.copy()
        expected_recordset['ttl'] = new_ttl
        updated_rs = RecordsetTestWrapper(self, expected_recordset)
        self.register_uris([
            # try by directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones'],
                     qs_elements=[
                         'name={name}'.format(name=fake_zone['name'])]),
                 json={'zones': [fake_zone.get_get_response_json()]}),
            # try directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets', fake_rs['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets'],
                     qs_elements=['name={name}'.format(name=fake_rs['name'])]),
                 json={'recordsets': [fake_rs.get_get_response_json()]}),
            # update
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets', fake_rs['id']]),
                 json=updated_rs.get_get_response_json(),
                 validate=dict(json={'ttl': new_ttl}))
        ])
        res = self.cloud.update_recordset(
            fake_zone['name'], fake_rs['name'], ttl=new_ttl)

        updated_rs.cmp(res)
        self.assert_calls()

    def test_list_recordsets(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        fake_rs = RecordsetTestWrapper(self, recordset)
        self.register_uris([
            # try by directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id']]),
                 json=fake_zone.get_get_response_json()),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'], 'recordsets']),
                 json={'recordsets': [fake_rs.get_get_response_json()],
                       'links': {
                           'next': self.get_mock_url(
                               'dns', 'public',
                               append=['v2', 'zones', fake_zone['id'],
                                       'recordsets?limit=1&marker=asd']),
                           'self': self.get_mock_url(
                               'dns', 'public',
                               append=['v2', 'zones', fake_zone['id'],
                                       'recordsets?limit=1'])},
                       'metadata':{'total_count': 2}}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'], 'recordsets'],
                     qs_elements=[
                        'limit=1', 'marker=asd']),
                 json={'recordsets': [fake_rs.get_get_response_json()]}),
        ])
        res = self.cloud.list_recordsets(fake_zone['id'])

        self.assertEqual(2, len(res))
        self.assert_calls()

    def test_delete_recordset(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        fake_rs = RecordsetTestWrapper(self, recordset)
        self.register_uris([
            # try by directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones'],
                     qs_elements=[
                        'name={name}'.format(name=fake_zone['name'])]),
                 json={'zones': [fake_zone.get_get_response_json()]}),
            # try directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets', fake_rs['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets'],
                     qs_elements=[
                        'name={name}'.format(name=fake_rs['name'])]),
                 json={'recordsets': [fake_rs.get_get_response_json()]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', zone['id'],
                             'recordsets', fake_rs['id']]),
                 status_code=202)
        ])
        self.assertTrue(
            self.cloud.delete_recordset(fake_zone['name'], fake_rs['name']))
        self.assert_calls()

    def test_get_recordset_by_id(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        fake_rs = RecordsetTestWrapper(self, recordset)
        self.register_uris([
            # try by directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones'],
                     qs_elements=[
                        'name={name}'.format(name=fake_zone['name'])]),
                 json={'zones': [fake_zone.get_get_response_json()]}),
            # try directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets', fake_rs['id']]),
                 json=fake_rs.get_get_response_json())
        ])
        res = self.cloud.get_recordset(fake_zone['name'], fake_rs['id'])
        fake_rs.cmp(res)
        self.assert_calls()

    def test_get_recordset_by_name(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        fake_rs = RecordsetTestWrapper(self, recordset)
        self.register_uris([
            # try by directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones'],
                     qs_elements=[
                        'name={name}'.format(name=fake_zone['name'])]),
                 json={'zones': [fake_zone.get_get_response_json()]}),
            # try directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets', fake_rs['name']]),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets'],
                     qs_elements=['name={name}'.format(name=fake_rs['name'])]),
                 json={'recordsets': [fake_rs.get_get_response_json()]})
        ])
        res = self.cloud.get_recordset(fake_zone['name'], fake_rs['name'])
        fake_rs.cmp(res)
        self.assert_calls()

    def test_get_recordset_not_found_returns_false(self):
        fake_zone = test_zone.ZoneTestWrapper(self, zone)
        self.register_uris([
            # try by directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones', fake_zone['id']]),
                 json=fake_zone.get_get_response_json()),
            # try directly
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets', 'fake']),
                 status_code=404),
            # list with name
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['v2', 'zones', fake_zone['id'],
                             'recordsets'],
                     qs_elements=['name=fake']),
                 json={'recordsets': []})
        ])
        res = self.cloud.get_recordset(fake_zone['id'], 'fake')
        self.assertFalse(res)
        self.assert_calls()
