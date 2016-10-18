# -*- coding: utf-8 -*-

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

from shade import _utils
from shade.tests.unit import base

RAW_SERVER_DICT = {
    'HUMAN_ID': True,
    'NAME_ATTR': 'name',
    'OS-DCF:diskConfig': u'MANUAL',
    'OS-EXT-AZ:availability_zone': u'ca-ymq-2',
    'OS-EXT-STS:power_state': 1,
    'OS-EXT-STS:task_state': None,
    'OS-EXT-STS:vm_state': u'active',
    'OS-SRV-USG:launched_at': u'2015-08-01T19:52:02.000000',
    'OS-SRV-USG:terminated_at': None,
    'accessIPv4': u'',
    'accessIPv6': u'',
    'addresses': {
        u'public': [{
            u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:9f:46:3e',
            u'OS-EXT-IPS:type': u'fixed',
            u'addr': u'2604:e100:1:0:f816:3eff:fe9f:463e',
            u'version': 6
        }, {
            u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:9f:46:3e',
            u'OS-EXT-IPS:type': u'fixed',
            u'addr': u'162.253.54.192',
            u'version': 4}]},
    'config_drive': u'True',
    'created': u'2015-08-01T19:52:16Z',
    'flavor': {
        u'id': u'bbcb7eb5-5c8d-498f-9d7e-307c575d3566',
        u'links': [{
            u'href': u'https://compute-ca-ymq-1.vexxhost.net/db9/flavors/bbc',
            u'rel': u'bookmark'}]},
    'hostId': u'bd37',
    'human_id': u'mordred-irc',
    'id': u'811c5197-dba7-4d3a-a3f6-68ca5328b9a7',
    'image': {
        u'id': u'69c99b45-cd53-49de-afdc-f24789eb8f83',
        u'links': [{
            u'href': u'https://compute-ca-ymq-1.vexxhost.net/db9/images/69c',
            u'rel': u'bookmark'}]},
    'key_name': u'mordred',
    'links': [{
        u'href': u'https://compute-ca-ymq-1.vexxhost.net/v2/db9/servers/811',
        u'rel': u'self'
    }, {
        u'href': u'https://compute-ca-ymq-1.vexxhost.net/db9/servers/811',
        u'rel': u'bookmark'}],
    'metadata': {u'group': u'irc', u'groups': u'irc,enabled'},
    'name': u'mordred-irc',
    'networks': {u'public': [u'2604:e100:1:0:f816:3eff:fe9f:463e',
                             u'162.253.54.192']},
    'os-extended-volumes:volumes_attached': [],
    'progress': 0,
    'request_ids': [],
    'security_groups': [{u'name': u'default'}],
    'status': u'ACTIVE',
    'tenant_id': u'db92b20496ae4fbda850a689ea9d563f',
    'updated': u'2016-10-15T15:49:29Z',
    'user_id': u'e9b21dc437d149858faee0898fb08e92'}


class TestUtils(base.TestCase):

    def test_normalize_servers_strict(self):
        raw_server = RAW_SERVER_DICT.copy()
        expected = {
            'accessIPv4': u'',
            'accessIPv6': u'',
            'addresses': {
                u'public': [{
                    u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:9f:46:3e',
                    u'OS-EXT-IPS:type': u'fixed',
                    u'addr': u'2604:e100:1:0:f816:3eff:fe9f:463e',
                    u'version': 6
                }, {
                    u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:9f:46:3e',
                    u'OS-EXT-IPS:type': u'fixed',
                    u'addr': u'162.253.54.192',
                    u'version': 4}]},
            'adminPass': None,
            'created': u'2015-08-01T19:52:16Z',
            'disk_config': u'MANUAL',
            'flavor': {u'id': u'bbcb7eb5-5c8d-498f-9d7e-307c575d3566'},
            'has_config_drive': True,
            'host_id': u'bd37',
            'id': u'811c5197-dba7-4d3a-a3f6-68ca5328b9a7',
            'image': {u'id': u'69c99b45-cd53-49de-afdc-f24789eb8f83'},
            'interface_ip': u'',
            'key_name': u'mordred',
            'launched_at': u'2015-08-01T19:52:02.000000',
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': None,
                    'id': u'db92b20496ae4fbda850a689ea9d563f',
                    'name': None},
                'region_name': u'RegionOne',
                'zone': u'ca-ymq-2'},
            'metadata': {u'group': u'irc', u'groups': u'irc,enabled'},
            'name': u'mordred-irc',
            'networks': {
                u'public': [
                    u'2604:e100:1:0:f816:3eff:fe9f:463e',
                    u'162.253.54.192']},
            'power_state': 1,
            'private_v4': None,
            'progress': 0,
            'properties': {
                'request_ids': []},
            'public_v4': None,
            'public_v6': None,
            'security_groups': [{u'name': u'default'}],
            'status': u'ACTIVE',
            'task_state': None,
            'terminated_at': None,
            'updated': u'2016-10-15T15:49:29Z',
            'user_id': u'e9b21dc437d149858faee0898fb08e92',
            'vm_state': u'active',
            'volumes': []}
        retval = self.strict_cloud._normalize_server(raw_server).toDict()
        self.assertEqual(expected, retval)

    def test_normalize_servers_normal(self):
        raw_server = RAW_SERVER_DICT.copy()
        expected = {
            'OS-DCF:diskConfig': u'MANUAL',
            'OS-EXT-AZ:availability_zone': u'ca-ymq-2',
            'OS-EXT-STS:power_state': 1,
            'OS-EXT-STS:task_state': None,
            'OS-EXT-STS:vm_state': u'active',
            'OS-SRV-USG:launched_at': u'2015-08-01T19:52:02.000000',
            'OS-SRV-USG:terminated_at': None,
            'accessIPv4': u'',
            'accessIPv6': u'',
            'addresses': {
                u'public': [{
                    u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:9f:46:3e',
                    u'OS-EXT-IPS:type': u'fixed',
                    u'addr': u'2604:e100:1:0:f816:3eff:fe9f:463e',
                    u'version': 6
                }, {
                    u'OS-EXT-IPS-MAC:mac_addr': u'fa:16:3e:9f:46:3e',
                    u'OS-EXT-IPS:type': u'fixed',
                    u'addr': u'162.253.54.192',
                    u'version': 4}]},
            'adminPass': None,
            'az': u'ca-ymq-2',
            'cloud': '_test_cloud_',
            'config_drive': u'True',
            'created': u'2015-08-01T19:52:16Z',
            'disk_config': u'MANUAL',
            'flavor': {u'id': u'bbcb7eb5-5c8d-498f-9d7e-307c575d3566'},
            'has_config_drive': True,
            'hostId': u'bd37',
            'host_id': u'bd37',
            'id': u'811c5197-dba7-4d3a-a3f6-68ca5328b9a7',
            'image': {u'id': u'69c99b45-cd53-49de-afdc-f24789eb8f83'},
            'interface_ip': '',
            'key_name': u'mordred',
            'launched_at': u'2015-08-01T19:52:02.000000',
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': None,
                    'id': u'db92b20496ae4fbda850a689ea9d563f',
                    'name': None},
                'region_name': u'RegionOne',
                'zone': u'ca-ymq-2'},
            'metadata': {u'group': u'irc', u'groups': u'irc,enabled'},
            'name': u'mordred-irc',
            'networks': {
                u'public': [
                    u'2604:e100:1:0:f816:3eff:fe9f:463e',
                    u'162.253.54.192']},
            'os-extended-volumes:volumes_attached': [],
            'power_state': 1,
            'private_v4': None,
            'progress': 0,
            'project_id': u'db92b20496ae4fbda850a689ea9d563f',
            'properties': {
                'OS-DCF:diskConfig': u'MANUAL',
                'OS-EXT-AZ:availability_zone': u'ca-ymq-2',
                'OS-EXT-STS:power_state': 1,
                'OS-EXT-STS:task_state': None,
                'OS-EXT-STS:vm_state': u'active',
                'OS-SRV-USG:launched_at': u'2015-08-01T19:52:02.000000',
                'OS-SRV-USG:terminated_at': None,
                'os-extended-volumes:volumes_attached': [],
                'request_ids': []},
            'public_v4': None,
            'public_v6': None,
            'region': u'RegionOne',
            'request_ids': [],
            'security_groups': [{u'name': u'default'}],
            'status': u'ACTIVE',
            'task_state': None,
            'tenant_id': u'db92b20496ae4fbda850a689ea9d563f',
            'terminated_at': None,
            'updated': u'2016-10-15T15:49:29Z',
            'user_id': u'e9b21dc437d149858faee0898fb08e92',
            'vm_state': u'active',
            'volumes': []}
        retval = self.cloud._normalize_server(raw_server).toDict()
        self.assertEqual(expected, retval)

    def test_normalize_secgroups_strict(self):
        nova_secgroup = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            rules=[
                dict(id='123', from_port=80, to_port=81, ip_protocol='tcp',
                     ip_range={'cidr': '0.0.0.0/0'}, parent_group_id='xyz123')
            ]
        )

        expected = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            properties={},
            location=dict(
                region_name='RegionOne',
                zone=None,
                project=dict(
                    domain_name=None,
                    id=mock.ANY,
                    domain_id=None,
                    name='admin'),
                cloud='_test_cloud_'),
            security_group_rules=[
                dict(id='123', direction='ingress', ethertype='IPv4',
                     port_range_min=80, port_range_max=81, protocol='tcp',
                     remote_ip_prefix='0.0.0.0/0', security_group_id='xyz123',
                     properties={},
                     remote_group_id=None,
                     location=dict(
                         region_name='RegionOne',
                         zone=None,
                         project=dict(
                             domain_name=None,
                             id=mock.ANY,
                             domain_id=None,
                             name='admin'),
                         cloud='_test_cloud_'))
            ]
        )

        retval = self.strict_cloud._normalize_secgroup(nova_secgroup)
        self.assertEqual(expected, retval)

    def test_normalize_secgroups(self):
        nova_secgroup = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            rules=[
                dict(id='123', from_port=80, to_port=81, ip_protocol='tcp',
                     ip_range={'cidr': '0.0.0.0/0'}, parent_group_id='xyz123')
            ]
        )

        expected = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            tenant_id='',
            project_id='',
            properties={},
            location=dict(
                region_name='RegionOne',
                zone=None,
                project=dict(
                    domain_name=None,
                    id=mock.ANY,
                    domain_id=None,
                    name='admin'),
                cloud='_test_cloud_'),
            security_group_rules=[
                dict(id='123', direction='ingress', ethertype='IPv4',
                     port_range_min=80, port_range_max=81, protocol='tcp',
                     remote_ip_prefix='0.0.0.0/0', security_group_id='xyz123',
                     properties={},
                     tenant_id='',
                     project_id='',
                     remote_group_id=None,
                     location=dict(
                         region_name='RegionOne',
                         zone=None,
                         project=dict(
                             domain_name=None,
                             id=mock.ANY,
                             domain_id=None,
                             name='admin'),
                         cloud='_test_cloud_'))
            ]
        )

        retval = self.cloud._normalize_secgroup(nova_secgroup)
        self.assertEqual(expected, retval)

    def test_normalize_secgroups_negone_port(self):
        nova_secgroup = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group with -1 ports',
            rules=[
                dict(id='123', from_port=-1, to_port=-1, ip_protocol='icmp',
                     ip_range={'cidr': '0.0.0.0/0'}, parent_group_id='xyz123')
            ]
        )

        retval = self.cloud._normalize_secgroup(nova_secgroup)
        self.assertIsNone(retval['security_group_rules'][0]['port_range_min'])
        self.assertIsNone(retval['security_group_rules'][0]['port_range_max'])

    def test_normalize_secgroup_rules(self):
        nova_rules = [
            dict(id='123', from_port=80, to_port=81, ip_protocol='tcp',
                 ip_range={'cidr': '0.0.0.0/0'}, parent_group_id='xyz123')
        ]
        expected = [
            dict(id='123', direction='ingress', ethertype='IPv4',
                 port_range_min=80, port_range_max=81, protocol='tcp',
                 remote_ip_prefix='0.0.0.0/0', security_group_id='xyz123',
                 tenant_id='', project_id='', remote_group_id=None,
                 properties={},
                 location=dict(
                     region_name='RegionOne',
                     zone=None,
                     project=dict(
                         domain_name=None,
                         id=mock.ANY,
                         domain_id=None,
                         name='admin'),
                     cloud='_test_cloud_'))
        ]
        retval = self.cloud._normalize_secgroup_rules(nova_rules)
        self.assertEqual(expected, retval)

    def test_normalize_volumes_v1(self):
        vol = dict(
            display_name='test',
            display_description='description',
            bootable=u'false',   # unicode type
            multiattach='true',  # str type
        )
        expected = dict(
            name=vol['display_name'],
            display_name=vol['display_name'],
            description=vol['display_description'],
            display_description=vol['display_description'],
            bootable=False,
            multiattach=True,
        )
        retval = _utils.normalize_volumes([vol])
        self.assertEqual([expected], retval)

    def test_normalize_volumes_v2(self):
        vol = dict(
            display_name='test',
            display_description='description',
            bootable=False,
            multiattach=True,
        )
        expected = dict(
            name=vol['display_name'],
            display_name=vol['display_name'],
            description=vol['display_description'],
            display_description=vol['display_description'],
            bootable=False,
            multiattach=True,
        )
        retval = _utils.normalize_volumes([vol])
        self.assertEqual([expected], retval)
