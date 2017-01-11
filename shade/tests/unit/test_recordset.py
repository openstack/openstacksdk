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


import mock
import testtools

import shade
from shade.tests.unit import base
from shade.tests import fakes

zone_obj = fakes.FakeZone(
    id='1',
    name='example.net.',
    type_='PRIMARY',
    email='test@example.net',
    description='Example zone',
    ttl=3600,
    masters=None
)

recordset_obj = fakes.FakeRecordset(
    zone='1',
    id='1',
    name='www.example.net.',
    type_='A',
    description='Example zone',
    ttl=3600,
    records=['192.168.1.1']
)


class TestRecordset(base.TestCase):

    def setUp(self):
        super(TestRecordset, self).setUp()

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_create_recordset(self, mock_designate):
        mock_designate.zones.list.return_value = [zone_obj]
        self.cloud.create_recordset(zone=recordset_obj.zone,
                                    name=recordset_obj.name,
                                    recordset_type=recordset_obj.type_,
                                    records=recordset_obj.records,
                                    description=recordset_obj.description,
                                    ttl=recordset_obj.ttl)
        mock_designate.recordsets.create.assert_called_once_with(
            zone=recordset_obj.zone, name=recordset_obj.name,
            type_=recordset_obj.type_.upper(),
            records=recordset_obj.records,
            description=recordset_obj.description,
            ttl=recordset_obj.ttl
        )

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_create_recordset_exception(self, mock_designate):
        mock_designate.zones.list.return_value = [zone_obj]
        mock_designate.recordsets.create.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Unable to create recordset www2.example.net."
        ):
            self.cloud.create_recordset('1', 'www2.example.net.',
                                        'a', ['192.168.1.2'])

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_update_recordset(self, mock_designate):
        new_ttl = 7200
        mock_designate.zones.list.return_value = [zone_obj]
        mock_designate.recordsets.list.return_value = [recordset_obj]
        self.cloud.update_recordset('1', '1', ttl=new_ttl)
        mock_designate.recordsets.update.assert_called_once_with(
            zone='1', recordset='1', values={'ttl': new_ttl}
        )

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_delete_recordset(self, mock_designate):
        mock_designate.zones.list.return_value = [zone_obj]
        mock_designate.recordsets.list.return_value = [recordset_obj]
        self.cloud.delete_recordset('1', '1')
        mock_designate.recordsets.delete.assert_called_once_with(
            zone='1', recordset='1'
        )

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_get_recordset_by_id(self, mock_designate):
        mock_designate.recordsets.get.return_value = recordset_obj
        recordset = self.cloud.get_recordset('1', '1')
        self.assertTrue(mock_designate.recordsets.get.called)
        self.assertEqual(recordset['id'], '1')

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_get_recordset_by_name(self, mock_designate):
        mock_designate.recordsets.get.return_value = recordset_obj
        recordset = self.cloud.get_recordset('1', 'www.example.net.')
        self.assertTrue(mock_designate.recordsets.get.called)
        self.assertEqual(recordset['name'], 'www.example.net.')

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_get_recordset_not_found_returns_false(self, mock_designate):
        mock_designate.recordsets.get.return_value = None
        recordset = self.cloud.get_recordset('1', 'www.nonexistingrecord.net.')
        self.assertFalse(recordset)
