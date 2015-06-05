# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import testtools
import warlock

from shade import meta

PRIVATE_V4 = '198.51.100.3'
PUBLIC_V4 = '192.0.2.99'


class FakeCloud(object):
    region_name = 'test-region'
    name = 'test-name'
    private = False
    service_val = True
    _unused = "useless"

    def get_flavor_name(self, id):
        return 'test-flavor-name'

    def get_image_name(self, id):
        return 'test-image-name'

    def get_volumes(self, server):
        return []

    def has_service(self, service_name):
        return self.service_val


class FakeServer(object):
    id = 'test-id-0'
    metadata = {'group': 'test-group'}
    addresses = {'private': [{'OS-EXT-IPS:type': 'fixed',
                              'addr': PRIVATE_V4,
                              'version': 4}],
                 'public': [{'OS-EXT-IPS:type': 'floating',
                             'addr': PUBLIC_V4,
                             'version': 4}]}
    flavor = {'id': '101'}
    image = {'id': '471c2475-da2f-47ac-aba5-cb4aa3d546f5'}


class TestMeta(testtools.TestCase):
    def test_find_nova_addresses_key_name(self):
        # Note 198.51.100.0/24 is TEST-NET-2 from rfc5737
        addrs = {'public': [{'addr': '198.51.100.1', 'version': 4}],
                 'private': [{'addr': '192.0.2.5', 'version': 4}]}
        self.assertEqual(
            ['198.51.100.1'],
            meta.find_nova_addresses(addrs, key_name='public'))
        self.assertEqual([], meta.find_nova_addresses(addrs, key_name='foo'))

    def test_find_nova_addresses_ext_tag(self):
        addrs = {'public': [{'OS-EXT-IPS:type': 'fixed',
                             'addr': '198.51.100.2',
                             'version': 4}]}
        self.assertEqual(
            ['198.51.100.2'], meta.find_nova_addresses(addrs, ext_tag='fixed'))
        self.assertEqual([], meta.find_nova_addresses(addrs, ext_tag='foo'))

    def test_get_server_ip(self):
        srv = FakeServer()
        self.assertEqual(PRIVATE_V4, meta.get_server_private_ip(srv))
        self.assertEqual(PUBLIC_V4, meta.get_server_public_ip(srv))

    def test_get_groups_from_server(self):
        server_vars = {'flavor': 'test-flavor',
                       'image': 'test-image',
                       'az': 'test-az'}
        self.assertEqual(
            ['test-name',
             'test-region',
             'test-name_test-region',
             'test-group',
             'instance-test-id-0',
             'meta-group_test-group',
             'test-az',
             'test-region_test-az',
             'test-name_test-region_test-az'],
            meta.get_groups_from_server(
                FakeCloud(), FakeServer(), server_vars))

    def test_obj_list_to_dict(self):
        """Test conversion of a list of objects to a list of dictonaries"""
        class obj0(object):
            value = 0

        class obj1(object):
            value = 1

        list = [obj0, obj1]
        new_list = meta.obj_list_to_dict(list)
        self.assertEqual(new_list[0]['value'], 0)
        self.assertEqual(new_list[1]['value'], 1)

    def test_basic_hostvars(self):
        hostvars = meta.get_hostvars_from_server(
            FakeCloud(), meta.obj_to_dict(FakeServer()))
        self.assertNotIn('links', hostvars)
        self.assertEqual(PRIVATE_V4, hostvars['private_v4'])
        self.assertEqual(PUBLIC_V4, hostvars['public_v4'])
        self.assertEqual(PUBLIC_V4, hostvars['interface_ip'])
        self.assertEquals(FakeCloud.region_name, hostvars['region'])
        self.assertEquals(FakeCloud.name, hostvars['cloud'])
        self.assertEquals("test-image-name", hostvars['image']['name'])
        self.assertEquals(FakeServer.image['id'], hostvars['image']['id'])
        self.assertNotIn('links', hostvars['image'])
        self.assertEquals(FakeServer.flavor['id'], hostvars['flavor']['id'])
        self.assertEquals("test-flavor-name", hostvars['flavor']['name'])
        self.assertNotIn('links', hostvars['flavor'])
        # test having volumes
        # test volume exception
        self.assertEquals([], hostvars['volumes'])

    def test_private_interface_ip(self):
        cloud = FakeCloud()
        cloud.private = True
        hostvars = meta.get_hostvars_from_server(
            cloud, meta.obj_to_dict(FakeServer()))
        self.assertEqual(PRIVATE_V4, hostvars['interface_ip'])

    def test_image_string(self):
        server = FakeServer()
        server.image = 'fake-image-id'
        hostvars = meta.get_hostvars_from_server(
            FakeCloud(), meta.obj_to_dict(server))
        self.assertEquals('fake-image-id', hostvars['image']['id'])

    def test_az(self):
        server = FakeServer()
        server.__dict__['OS-EXT-AZ:availability_zone'] = 'az1'
        hostvars = meta.get_hostvars_from_server(
            FakeCloud(), meta.obj_to_dict(server))
        self.assertEquals('az1', hostvars['az'])

    def test_has_volume(self):
        mock_cloud = mock.MagicMock()
        mock_volume = mock.MagicMock()
        mock_volume.id = 'volume1'
        mock_volume.status = 'available'
        mock_volume.display_name = 'Volume 1 Display Name'
        mock_volume.attachments = [{'device': '/dev/sda0'}]
        mock_volume_dict = meta.obj_to_dict(mock_volume)
        mock_cloud.get_volumes.return_value = [mock_volume_dict]
        hostvars = meta.get_hostvars_from_server(
            mock_cloud, meta.obj_to_dict(FakeServer()))
        self.assertEquals('volume1', hostvars['volumes'][0]['id'])
        self.assertEquals('/dev/sda0', hostvars['volumes'][0]['device'])

    def test_has_no_volume_service(self):
        fake_cloud = FakeCloud()
        fake_cloud.service_val = False
        hostvars = meta.get_hostvars_from_server(
            fake_cloud, meta.obj_to_dict(FakeServer()))
        self.assertEquals([], hostvars['volumes'])

    def test_unknown_volume_exception(self):
        mock_cloud = mock.MagicMock()

        class FakeException(Exception):
            pass

        def side_effect(*args):
            raise FakeException("No Volumes")
        mock_cloud.get_volumes.side_effect = side_effect
        self.assertRaises(
            FakeException,
            meta.get_hostvars_from_server,
            mock_cloud,
            meta.obj_to_dict(FakeServer()))

    def test_obj_to_dict(self):
        cloud = FakeCloud()
        cloud.server = FakeServer()
        cloud_dict = meta.obj_to_dict(cloud)
        self.assertEqual(FakeCloud.name, cloud_dict['name'])
        self.assertNotIn('_unused', cloud_dict)
        self.assertNotIn('get_flavor_name', cloud_dict)
        self.assertNotIn('server', cloud_dict)
        self.assertTrue(hasattr(cloud_dict, 'name'))
        self.assertEquals(cloud_dict.name, cloud_dict['name'])

    def test_warlock_to_dict(self):
        schema = {
            'name': 'Test',
            'properties': {
                'id': {'type': 'string'},
                'name': {'type': 'string'},
                '_unused': {'type': 'string'},
            }
        }
        test_model = warlock.model_factory(schema)
        test_obj = test_model(
            id='471c2475-da2f-47ac-aba5-cb4aa3d546f5',
            name='test-image')
        test_dict = meta.warlock_to_dict(test_obj)
        self.assertNotIn('_unused', test_dict)
        self.assertEqual('test-image', test_dict['name'])
        self.assertTrue(hasattr(test_dict, 'name'))
        self.assertEquals(test_dict.name, test_dict['name'])
