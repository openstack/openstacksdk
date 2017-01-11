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


class TestZone(base.TestCase):

    def setUp(self):
        super(TestZone, self).setUp()
        self.cloud = shade.openstack_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_create_zone(self, mock_designate):
        self.cloud.create_zone(name=zone_obj.name, zone_type=zone_obj.type_,
                               email=zone_obj.email,
                               description=zone_obj.description,
                               ttl=zone_obj.ttl, masters=zone_obj.masters)
        mock_designate.zones.create.assert_called_once_with(
            name=zone_obj.name, type_=zone_obj.type_.upper(),
            email=zone_obj.email, description=zone_obj.description,
            ttl=zone_obj.ttl, masters=zone_obj.masters
        )

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_create_zone_exception(self, mock_designate):
        mock_designate.zones.create.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Unable to create zone example.net."
        ):
            self.cloud.create_zone('example.net.')

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_update_zone(self, mock_designate):
        new_ttl = 7200
        mock_designate.zones.list.return_value = [zone_obj]
        self.cloud.update_zone('1', ttl=new_ttl)
        mock_designate.zones.update.assert_called_once_with(
            zone='1', values={'ttl': new_ttl}
        )

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_delete_zone(self, mock_designate):
        mock_designate.zones.list.return_value = [zone_obj]
        self.cloud.delete_zone('1')
        mock_designate.zones.delete.assert_called_once_with(
            zone='1'
        )

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_get_zone_by_id(self, mock_designate):
        mock_designate.zones.list.return_value = [zone_obj]
        zone = self.cloud.get_zone('1')
        self.assertTrue(mock_designate.zones.list.called)
        self.assertEqual(zone['id'], '1')

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_get_zone_by_name(self, mock_designate):
        mock_designate.zones.list.return_value = [zone_obj]
        zone = self.cloud.get_zone('example.net.')
        self.assertTrue(mock_designate.zones.list.called)
        self.assertEqual(zone['name'], 'example.net.')

    @mock.patch.object(shade.OpenStackCloud, 'designate_client')
    def test_get_zone_not_found_returns_false(self, mock_designate):
        mock_designate.zones.list.return_value = []
        zone = self.cloud.get_zone('nonexistingzone.net.')
        self.assertFalse(zone)
