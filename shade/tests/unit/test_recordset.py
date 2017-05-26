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

import shade
from shade.tests.unit import base


zone = {
    'id': '1',
    'name': 'example.net.',
    'type': 'PRIMARY',
    'email': 'test@example.net',
    'description': 'Example zone',
    'ttl': 3600,
}

recordset = {
    'name': 'www.example.net.',
    'type': 'A',
    'description': 'Example zone',
    'ttl': 3600,
    'records': ['192.168.1.1']
}
recordset_zone = '1'

new_recordset = copy.copy(recordset)
new_recordset['id'] = '1'
new_recordset['zone'] = recordset_zone


class TestRecordset(base.RequestsMockTestCase):

    def test_create_recordset(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [zone],
                     "links": {},
                     "metadata": {
                         'total_count': 1}}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones', zone['id']]),
                 json=zone),
            self.get_designate_discovery_mock_dict(),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets']),
                 json=new_recordset,
                 validate=dict(json=recordset)),
        ])
        rs = self.cloud.create_recordset(
            zone=recordset_zone,
            name=recordset['name'],
            recordset_type=recordset['type'],
            records=recordset['records'],
            description=recordset['description'],
            ttl=recordset['ttl'])
        self.assertEqual(new_recordset, rs)
        self.assert_calls()

    def test_create_recordset_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [zone],
                     "links": {},
                     "metadata": {
                         'total_count': 1}}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones', zone['id']]),
                 json=zone),
            self.get_designate_discovery_mock_dict(),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets']),
                 status_code=500,
                 validate=dict(json={
                     'name': 'www2.example.net.',
                     'records': ['192.168.1.2'],
                     'type': 'A'})),
        ])
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Unable to create recordset www2.example.net."
        ):
            self.cloud.create_recordset('1', 'www2.example.net.',
                                        'a', ['192.168.1.2'])
        self.assert_calls()

    def test_update_recordset(self):
        new_ttl = 7200
        expected_recordset = {
            'name': recordset['name'],
            'records': recordset['records'],
            'type': recordset['type']
        }
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [zone],
                     "links": {},
                     "metadata": {
                         'total_count': 1}}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets'],
                     qs_elements=['name={0}'.format(
                         new_recordset['id'])]),
                 json={"recordsets": [new_recordset]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'],
                             'recordsets', new_recordset['id']]),
                 json={"recordsets": [new_recordset]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets'],
                     qs_elements=['name={0}'.format(
                         new_recordset['id'])]),
                 json={"recordsets": [new_recordset]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'],
                             'recordsets', new_recordset['id']]),
                 json=expected_recordset,
                 validate=dict(json={'ttl': new_ttl}))
        ])
        updated_rs = self.cloud.update_recordset('1', '1', ttl=new_ttl)
        self.assertEqual(expected_recordset, updated_rs)
        self.assert_calls()

    def test_delete_recordset(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['v2', 'zones']),
                 json={
                     "zones": [zone],
                     "links": {},
                     "metadata": {
                         'total_count': 1}}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets'],
                     qs_elements=['name={0}'.format(
                         new_recordset['id'])]),
                 json={"recordsets": [new_recordset]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'],
                             'recordsets', new_recordset['id']]),
                 json={"recordsets": [new_recordset]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets'],
                     qs_elements=['name={0}'.format(
                         new_recordset['id'])]),
                 json={"recordsets": [new_recordset]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'],
                             'recordsets', new_recordset['id']]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_recordset('1', '1'))
        self.assert_calls()

    def _prepare_get_recordset_calls(self, zone_id, name_or_id):
        self.register_uris([
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets'],
                     qs_elements=['name={0}'.format(name_or_id)]),
                 json={"recordsets": [new_recordset]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'],
                             'recordsets', new_recordset['id']]),
                 json=new_recordset),
        ])

    def test_get_recordset_by_id(self):
        recordset = self._prepare_get_recordset_calls('1', '1')
        recordset = self.cloud.get_recordset('1', '1')
        self.assertEqual(recordset['id'], '1')
        self.assert_calls()

    def test_get_recordset_by_name(self):
        self._prepare_get_recordset_calls('1', new_recordset['name'])
        recordset = self.cloud.get_recordset('1', new_recordset['name'])
        self.assertEqual(new_recordset['name'], recordset['name'])
        self.assert_calls()

    def test_get_recordset_not_found_returns_false(self):
        recordset_name = "www.nonexistingrecord.net."
        self.register_uris([
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public', append=['zones'],
                     qs_elements=['name={0}'.format(zone['id'])]),
                 json={"zones": [zone]}),
            self.get_designate_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'dns', 'public',
                     append=['zones', zone['id'], 'recordsets'],
                     qs_elements=['name={0}'.format(recordset_name)]),
                 json=[])
        ])
        recordset = self.cloud.get_recordset('1', recordset_name)
        self.assertFalse(recordset)
        self.assert_calls()
