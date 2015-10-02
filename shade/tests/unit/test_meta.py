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

from neutronclient.common import exceptions as neutron_exceptions

import shade
from shade import meta
from shade import _utils
from shade.tests import fakes

PRIVATE_V4 = '198.51.100.3'
PUBLIC_V4 = '192.0.2.99'
PUBLIC_V6 = '2001:0db8:face:0da0:face::0b00:1c'  # rfc3849


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

    def use_internal_network(self):
        return True

    def use_external_network(self):
        return True

    def get_internal_network(self):
        return None

    def get_external_network(self):
        return None


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
    accessIPv4 = ''
    accessIPv6 = ''


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

    def test_find_nova_addresses_key_name_and_ext_tag(self):
        addrs = {'public': [{'OS-EXT-IPS:type': 'fixed',
                             'addr': '198.51.100.2',
                             'version': 4}]}
        self.assertEqual(
            ['198.51.100.2'], meta.find_nova_addresses(
                addrs, key_name='public', ext_tag='fixed'))
        self.assertEqual([], meta.find_nova_addresses(
            addrs, key_name='public', ext_tag='foo'))
        self.assertEqual([], meta.find_nova_addresses(
            addrs, key_name='bar', ext_tag='fixed'))

    def test_find_nova_addresses_all(self):
        addrs = {'public': [{'OS-EXT-IPS:type': 'fixed',
                             'addr': '198.51.100.2',
                             'version': 4}]}
        self.assertEqual(
            ['198.51.100.2'], meta.find_nova_addresses(
                addrs, key_name='public', ext_tag='fixed', version=4))
        self.assertEqual([], meta.find_nova_addresses(
            addrs, key_name='public', ext_tag='fixed', version=6))

    def test_get_server_ip(self):
        srv = meta.obj_to_dict(FakeServer())
        cloud = shade.openstack_cloud(validate=False)
        self.assertEqual(PRIVATE_V4, meta.get_server_private_ip(srv, cloud))
        self.assertEqual(PUBLIC_V4, meta.get_server_external_ipv4(cloud, srv))

    @mock.patch.object(shade.OpenStackCloud, 'has_service')
    @mock.patch.object(shade.OpenStackCloud, 'search_ports')
    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    def test_get_server_private_ip(self, mock_search_networks,
                                   mock_search_ports, mock_has_service):
        mock_has_service.return_value = True
        mock_search_ports.return_value = [{
            'network_id': 'test-net-id',
            'fixed_ips': [{'ip_address': PRIVATE_V4}],
            'device_id': 'test-id'
        }]
        mock_search_networks.return_value = [{
            'id': 'test-net-id',
            'name': 'test-net-name'
        }]

        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE',
            addresses={'private': [{'OS-EXT-IPS:type': 'fixed',
                                    'addr': PRIVATE_V4,
                                    'version': 4}],
                       'public': [{'OS-EXT-IPS:type': 'floating',
                                   'addr': PUBLIC_V4,
                                   'version': 4}]}
        ))
        cloud = shade.openstack_cloud(validate=False)

        self.assertEqual(PRIVATE_V4, meta.get_server_private_ip(srv, cloud))
        mock_has_service.assert_called_with('network')
        mock_search_ports.assert_called_once_with(
            filters={'device_id': 'test-id'}
        )
        mock_search_networks.assert_called_with(
            filters={'router:external': False, 'shared': False}
        )

    @mock.patch.object(shade.OpenStackCloud, 'has_service')
    @mock.patch.object(shade.OpenStackCloud, 'search_ports')
    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(meta, 'get_server_ip')
    def test_get_server_external_ipv4_neutron(
            self, mock_get_server_ip, mock_search_networks,
            mock_search_ports, mock_has_service):
        # Testing Clouds with Neutron
        mock_has_service.return_value = True
        mock_search_ports.return_value = [{
            'network_id': 'test-net-id',
            'fixed_ips': [{'ip_address': PUBLIC_V4}],
            'device_id': 'test-id'
        }]
        mock_search_networks.return_value = [{'id': 'test-net-id'}]

        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE'))
        ip = meta.get_server_external_ipv4(
            cloud=shade.openstack_cloud(validate=False), server=srv)

        self.assertEqual(PUBLIC_V4, ip)
        self.assertFalse(mock_get_server_ip.called)

    def test_get_server_external_ipv4_neutron_accessIPv4(self):
        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE',
            accessIPv4=PUBLIC_V4))
        ip = meta.get_server_external_ipv4(
            cloud=shade.openstack_cloud(validate=False), server=srv)

        self.assertEqual(PUBLIC_V4, ip)

    def test_get_server_external_ipv4_neutron_accessIPv6(self):
        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE',
            accessIPv6=PUBLIC_V6))
        ip = meta.get_server_external_ipv6(server=srv)

        self.assertEqual(PUBLIC_V6, ip)

    @mock.patch.object(shade.OpenStackCloud, 'has_service')
    @mock.patch.object(shade.OpenStackCloud, 'search_networks')
    @mock.patch.object(shade.OpenStackCloud, 'search_ports')
    @mock.patch.object(meta, 'get_server_ip')
    def test_get_server_external_ipv4_neutron_exception(
            self, mock_get_server_ip, mock_search_ports,
            mock_search_networks,
            mock_has_service):
        # Testing Clouds with a non working Neutron
        mock_has_service.return_value = True
        mock_search_networks.return_value = []
        mock_search_ports.side_effect = neutron_exceptions.NotFound()
        mock_get_server_ip.return_value = PUBLIC_V4

        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE'))
        ip = meta.get_server_external_ipv4(
            cloud=shade.openstack_cloud(validate=False), server=srv)

        self.assertEqual(PUBLIC_V4, ip)
        self.assertTrue(mock_get_server_ip.called)

    @mock.patch.object(shade.OpenStackCloud, 'has_service')
    @mock.patch.object(meta, 'get_server_ip')
    @mock.patch.object(_utils, 'is_globally_routable_ipv4')
    def test_get_server_external_ipv4_nova_public(
            self, mock_is_globally_routable_ipv4,
            mock_get_server_ip, mock_has_service):
        # Testing Clouds w/o Neutron and a network named public
        mock_has_service.return_value = False
        mock_get_server_ip.return_value = None
        mock_is_globally_routable_ipv4.return_value = True

        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE',
            addresses={'test-net': [{'addr': PUBLIC_V4}]}))
        ip = meta.get_server_external_ipv4(
            cloud=shade.openstack_cloud(validate=False), server=srv)

        self.assertEqual(PUBLIC_V4, ip)
        self.assertTrue(mock_get_server_ip.called)
        self.assertTrue(mock_is_globally_routable_ipv4.called)

    @mock.patch.object(shade.OpenStackCloud, 'has_service')
    @mock.patch.object(meta, 'get_server_ip')
    @mock.patch.object(_utils, 'is_globally_routable_ipv4')
    def test_get_server_external_ipv4_nova_none(
            self, mock_is_globally_routable_ipv4,
            mock_get_server_ip, mock_has_service):
        # Testing Clouds w/o Neutron and a globally routable IP
        mock_has_service.return_value = False
        mock_get_server_ip.return_value = None
        mock_is_globally_routable_ipv4.return_value = False

        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE',
            addresses={'test-net': [{'addr': PRIVATE_V4}]}))
        ip = meta.get_server_external_ipv4(
            cloud=shade.openstack_cloud(validate=False), server=srv)

        self.assertIsNone(ip)
        self.assertTrue(mock_get_server_ip.called)
        self.assertTrue(mock_is_globally_routable_ipv4.called)

    def test_get_server_external_ipv6(self):
        srv = meta.obj_to_dict(fakes.FakeServer(
            id='test-id', name='test-name', status='ACTIVE',
            addresses={
                'test-net': [
                    {'addr': PUBLIC_V4, 'version': 4},
                    {'addr': PUBLIC_V6, 'version': 6}
                ]
            }
        ))
        ip = meta.get_server_external_ipv6(srv)
        self.assertEqual(PUBLIC_V6, ip)

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
                FakeCloud(), meta.obj_to_dict(FakeServer()), server_vars))

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

    @mock.patch.object(shade.meta, 'get_server_external_ipv6')
    @mock.patch.object(shade.meta, 'get_server_external_ipv4')
    def test_basic_hostvars(
            self, mock_get_server_external_ipv4,
            mock_get_server_external_ipv6):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4
        mock_get_server_external_ipv6.return_value = PUBLIC_V6

        hostvars = meta.get_hostvars_from_server(
            FakeCloud(), meta.obj_to_dict(FakeServer()))
        self.assertNotIn('links', hostvars)
        self.assertEqual(PRIVATE_V4, hostvars['private_v4'])
        self.assertEqual(PUBLIC_V4, hostvars['public_v4'])
        self.assertEqual(PUBLIC_V6, hostvars['public_v6'])
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

    @mock.patch.object(shade.meta, 'get_server_external_ipv4')
    def test_private_interface_ip(self, mock_get_server_external_ipv4):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4

        cloud = FakeCloud()
        cloud.private = True
        hostvars = meta.get_hostvars_from_server(
            cloud, meta.obj_to_dict(FakeServer()))
        self.assertEqual(PRIVATE_V4, hostvars['interface_ip'])

    @mock.patch.object(shade.meta, 'get_server_external_ipv4')
    def test_image_string(self, mock_get_server_external_ipv4):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4

        server = FakeServer()
        server.image = 'fake-image-id'
        hostvars = meta.get_hostvars_from_server(
            FakeCloud(), meta.obj_to_dict(server))
        self.assertEquals('fake-image-id', hostvars['image']['id'])

    @mock.patch.object(shade.meta, 'get_server_external_ipv4')
    def test_az(self, mock_get_server_external_ipv4):
        mock_get_server_external_ipv4.return_value = PUBLIC_V4

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
