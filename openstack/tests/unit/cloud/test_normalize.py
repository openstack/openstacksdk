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

from openstack.compute.v2 import server as server_resource
from openstack.tests.unit import base

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

RAW_GLANCE_IMAGE_DICT = {
    u'auto_disk_config': u'False',
    u'checksum': u'774f48af604ab1ec319093234c5c0019',
    u'com.rackspace__1__build_core': u'1',
    u'com.rackspace__1__build_managed': u'1',
    u'com.rackspace__1__build_rackconnect': u'1',
    u'com.rackspace__1__options': u'0',
    u'com.rackspace__1__source': u'import',
    u'com.rackspace__1__visible_core': u'1',
    u'com.rackspace__1__visible_managed': u'1',
    u'com.rackspace__1__visible_rackconnect': u'1',
    u'container_format': u'ovf',
    u'created_at': u'2015-02-15T22:58:45Z',
    u'disk_format': u'vhd',
    u'file': u'/v2/images/f2868d7c-63e1-4974-a64d-8670a86df21e/file',
    u'id': u'f2868d7c-63e1-4974-a64d-8670a86df21e',
    u'image_type': u'import',
    u'min_disk': 20,
    u'min_ram': 0,
    u'name': u'Test Monty Ubuntu',
    u'org.openstack__1__architecture': u'x64',
    u'os_type': u'linux',
    u'owner': u'610275',
    u'protected': False,
    u'schema': u'/v2/schemas/image',
    u'size': 323004185,
    u'status': u'active',
    u'tags': [],
    u'updated_at': u'2015-02-15T23:04:34Z',
    u'user_id': u'156284',
    u'virtual_size': None,
    u'visibility': u'private',
    u'vm_mode': u'hvm',
    u'xenapi_use_agent': u'False'}

RAW_NOVA_IMAGE_DICT = {
    'HUMAN_ID': True,
    'NAME_ATTR': 'name',
    'OS-DCF:diskConfig': u'MANUAL',
    'OS-EXT-IMG-SIZE:size': 323004185,
    'created': u'2015-02-15T22:58:45Z',
    'human_id': u'test-monty-ubuntu',
    'id': u'f2868d7c-63e1-4974-a64d-8670a86df21e',
    'links': [{
        u'href': u'https://example.com/v2/610275/images/f2868d7c',
        u'rel': u'self'
    }, {
        u'href': u'https://example.com/610275/images/f2868d7c',
        u'rel': u'bookmark'
    }, {
        u'href': u'https://example.com/images/f2868d7c',
        u'rel': u'alternate',
        u'type': u'application/vnd.openstack.image'}],
    'metadata': {
        u'auto_disk_config': u'False',
        u'com.rackspace__1__build_core': u'1',
        u'com.rackspace__1__build_managed': u'1',
        u'com.rackspace__1__build_rackconnect': u'1',
        u'com.rackspace__1__options': u'0',
        u'com.rackspace__1__source': u'import',
        u'com.rackspace__1__visible_core': u'1',
        u'com.rackspace__1__visible_managed': u'1',
        u'com.rackspace__1__visible_rackconnect': u'1',
        u'image_type': u'import',
        u'org.openstack__1__architecture': u'x64',
        u'os_type': u'linux',
        u'user_id': u'156284',
        u'vm_mode': u'hvm',
        u'xenapi_use_agent': u'False'},
    'minDisk': 20,
    'minRam': 0,
    'name': u'Test Monty Ubuntu',
    'progress': 100,
    'request_ids': [],
    'status': u'ACTIVE',
    'updated': u'2015-02-15T23:04:34Z'}

RAW_FLAVOR_DICT = {
    'HUMAN_ID': True,
    'NAME_ATTR': 'name',
    'OS-FLV-EXT-DATA:ephemeral': 80,
    'OS-FLV-WITH-EXT-SPECS:extra_specs': {
        u'class': u'performance1',
        u'disk_io_index': u'40',
        u'number_of_data_disks': u'1',
        u'policy_class': u'performance_flavor',
        u'resize_policy_class': u'performance_flavor'},
    'disk': 40,
    'ephemeral': 80,
    'human_id': u'8-gb-performance',
    'id': u'performance1-8',
    'is_public': 'N/A',
    'links': [{
        u'href': u'https://example.com/v2/610275/flavors/performance1-8',
        u'rel': u'self'
    }, {
        u'href': u'https://example.com/610275/flavors/performance1-8',
        u'rel': u'bookmark'}],
    'name': u'8 GB Performance',
    'ram': 8192,
    'request_ids': [],
    'rxtx_factor': 1600.0,
    'swap': u'',
    'vcpus': 8}


def _assert_server_munch_attributes(testcase, raw, server):
    testcase.assertEqual(server.flavor.id, raw['flavor']['id'])
    testcase.assertEqual(server.image.id, raw['image']['id'])
    testcase.assertEqual(server.metadata.group, raw['metadata']['group'])
    testcase.assertEqual(
        server.security_groups[0].name,
        raw['security_groups'][0]['name'])


class TestNormalize(base.TestCase):

    def test_normalize_flavors(self):
        raw_flavor = RAW_FLAVOR_DICT.copy()
        expected = {
            'OS-FLV-EXT-DATA:ephemeral': 80,
            'OS-FLV-WITH-EXT-SPECS:extra_specs': {
                u'class': u'performance1',
                u'disk_io_index': u'40',
                u'number_of_data_disks': u'1',
                u'policy_class': u'performance_flavor',
                u'resize_policy_class': u'performance_flavor'},
            'disk': 40,
            'ephemeral': 80,
            'extra_specs': {
                u'class': u'performance1',
                u'disk_io_index': u'40',
                u'number_of_data_disks': u'1',
                u'policy_class': u'performance_flavor',
                u'resize_policy_class': u'performance_flavor'},
            'id': u'performance1-8',
            'is_disabled': False,
            'is_public': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': 'default',
                    'id': '1c36b64c840a42cd9e9b931a369337f0',
                    'name': 'admin'},
                'region_name': u'RegionOne',
                'zone': None},
            'name': u'8 GB Performance',
            'properties': {
                'OS-FLV-EXT-DATA:ephemeral': 80,
                'OS-FLV-WITH-EXT-SPECS:extra_specs': {
                    u'class': u'performance1',
                    u'disk_io_index': u'40',
                    u'number_of_data_disks': u'1',
                    u'policy_class': u'performance_flavor',
                    u'resize_policy_class': u'performance_flavor'}},
            'ram': 8192,
            'rxtx_factor': 1600.0,
            'swap': 0,
            'vcpus': 8}
        retval = self.cloud._normalize_flavor(raw_flavor)
        self.assertEqual(expected, retval)

    def test_normalize_nova_images(self):
        raw_image = RAW_NOVA_IMAGE_DICT.copy()
        expected = {
            u'auto_disk_config': u'False',
            u'com.rackspace__1__build_core': u'1',
            u'com.rackspace__1__build_managed': u'1',
            u'com.rackspace__1__build_rackconnect': u'1',
            u'com.rackspace__1__options': u'0',
            u'com.rackspace__1__source': u'import',
            u'com.rackspace__1__visible_core': u'1',
            u'com.rackspace__1__visible_managed': u'1',
            u'com.rackspace__1__visible_rackconnect': u'1',
            u'image_type': u'import',
            u'org.openstack__1__architecture': u'x64',
            u'os_type': u'linux',
            u'user_id': u'156284',
            u'vm_mode': u'hvm',
            u'xenapi_use_agent': u'False',
            'OS-DCF:diskConfig': u'MANUAL',
            'checksum': None,
            'container_format': None,
            'created': u'2015-02-15T22:58:45Z',
            'created_at': '2015-02-15T22:58:45Z',
            'direct_url': None,
            'disk_format': None,
            'file': None,
            'id': u'f2868d7c-63e1-4974-a64d-8670a86df21e',
            'is_protected': False,
            'is_public': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': 'default',
                    'id': '1c36b64c840a42cd9e9b931a369337f0',
                    'name': 'admin'},
                'region_name': u'RegionOne',
                'zone': None},
            'locations': [],
            'metadata': {
                u'auto_disk_config': u'False',
                u'com.rackspace__1__build_core': u'1',
                u'com.rackspace__1__build_managed': u'1',
                u'com.rackspace__1__build_rackconnect': u'1',
                u'com.rackspace__1__options': u'0',
                u'com.rackspace__1__source': u'import',
                u'com.rackspace__1__visible_core': u'1',
                u'com.rackspace__1__visible_managed': u'1',
                u'com.rackspace__1__visible_rackconnect': u'1',
                u'image_type': u'import',
                u'org.openstack__1__architecture': u'x64',
                u'os_type': u'linux',
                u'user_id': u'156284',
                u'vm_mode': u'hvm',
                u'xenapi_use_agent': u'False',
                'OS-DCF:diskConfig': u'MANUAL',
                'progress': 100},
            'minDisk': 20,
            'minRam': 0,
            'min_disk': 20,
            'min_ram': 0,
            'name': u'Test Monty Ubuntu',
            'owner': None,
            'progress': 100,
            'properties': {
                u'auto_disk_config': u'False',
                u'com.rackspace__1__build_core': u'1',
                u'com.rackspace__1__build_managed': u'1',
                u'com.rackspace__1__build_rackconnect': u'1',
                u'com.rackspace__1__options': u'0',
                u'com.rackspace__1__source': u'import',
                u'com.rackspace__1__visible_core': u'1',
                u'com.rackspace__1__visible_managed': u'1',
                u'com.rackspace__1__visible_rackconnect': u'1',
                u'image_type': u'import',
                u'org.openstack__1__architecture': u'x64',
                u'os_type': u'linux',
                u'user_id': u'156284',
                u'vm_mode': u'hvm',
                u'xenapi_use_agent': u'False',
                'OS-DCF:diskConfig': u'MANUAL',
                'progress': 100},
            'protected': False,
            'size': 323004185,
            'status': u'active',
            'tags': [],
            'updated': u'2015-02-15T23:04:34Z',
            'updated_at': u'2015-02-15T23:04:34Z',
            'virtual_size': 0,
            'visibility': 'private'}
        retval = self.cloud._normalize_image(raw_image)
        self.assertEqual(expected, retval)

    def test_normalize_glance_images(self):
        raw_image = RAW_GLANCE_IMAGE_DICT.copy()
        expected = {
            u'auto_disk_config': u'False',
            'checksum': u'774f48af604ab1ec319093234c5c0019',
            u'com.rackspace__1__build_core': u'1',
            u'com.rackspace__1__build_managed': u'1',
            u'com.rackspace__1__build_rackconnect': u'1',
            u'com.rackspace__1__options': u'0',
            u'com.rackspace__1__source': u'import',
            u'com.rackspace__1__visible_core': u'1',
            u'com.rackspace__1__visible_managed': u'1',
            u'com.rackspace__1__visible_rackconnect': u'1',
            'container_format': u'ovf',
            'created': u'2015-02-15T22:58:45Z',
            'created_at': u'2015-02-15T22:58:45Z',
            'direct_url': None,
            'disk_format': u'vhd',
            'file': u'/v2/images/f2868d7c-63e1-4974-a64d-8670a86df21e/file',
            'id': u'f2868d7c-63e1-4974-a64d-8670a86df21e',
            u'image_type': u'import',
            'is_protected': False,
            'is_public': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': None,
                    'id': u'610275',
                    'name': None},
                'region_name': u'RegionOne',
                'zone': None},
            'locations': [],
            'metadata': {
                u'auto_disk_config': u'False',
                u'com.rackspace__1__build_core': u'1',
                u'com.rackspace__1__build_managed': u'1',
                u'com.rackspace__1__build_rackconnect': u'1',
                u'com.rackspace__1__options': u'0',
                u'com.rackspace__1__source': u'import',
                u'com.rackspace__1__visible_core': u'1',
                u'com.rackspace__1__visible_managed': u'1',
                u'com.rackspace__1__visible_rackconnect': u'1',
                u'image_type': u'import',
                u'org.openstack__1__architecture': u'x64',
                u'os_type': u'linux',
                u'schema': u'/v2/schemas/image',
                u'user_id': u'156284',
                u'vm_mode': u'hvm',
                u'xenapi_use_agent': u'False'},
            'minDisk': 20,
            'min_disk': 20,
            'minRam': 0,
            'min_ram': 0,
            'name': u'Test Monty Ubuntu',
            u'org.openstack__1__architecture': u'x64',
            u'os_type': u'linux',
            'owner': u'610275',
            'properties': {
                u'auto_disk_config': u'False',
                u'com.rackspace__1__build_core': u'1',
                u'com.rackspace__1__build_managed': u'1',
                u'com.rackspace__1__build_rackconnect': u'1',
                u'com.rackspace__1__options': u'0',
                u'com.rackspace__1__source': u'import',
                u'com.rackspace__1__visible_core': u'1',
                u'com.rackspace__1__visible_managed': u'1',
                u'com.rackspace__1__visible_rackconnect': u'1',
                u'image_type': u'import',
                u'org.openstack__1__architecture': u'x64',
                u'os_type': u'linux',
                u'schema': u'/v2/schemas/image',
                u'user_id': u'156284',
                u'vm_mode': u'hvm',
                u'xenapi_use_agent': u'False'},
            'protected': False,
            u'schema': u'/v2/schemas/image',
            'size': 323004185,
            'status': u'active',
            'tags': [],
            'updated': u'2015-02-15T23:04:34Z',
            'updated_at': u'2015-02-15T23:04:34Z',
            u'user_id': u'156284',
            'virtual_size': 0,
            'visibility': u'private',
            u'vm_mode': u'hvm',
            u'xenapi_use_agent': u'False'}
        retval = self.cloud._normalize_image(raw_image)
        self.assertEqual(expected, retval)

    def test_normalize_servers_normal(self):
        res = server_resource.Server(
            connection=self.cloud,
            **RAW_SERVER_DICT)
        expected = {
            'OS-DCF:diskConfig': u'MANUAL',
            'OS-EXT-AZ:availability_zone': u'ca-ymq-2',
            'OS-EXT-SRV-ATTR:hypervisor_hostname': None,
            'OS-EXT-SRV-ATTR:instance_name': None,
            'OS-EXT-SRV-ATTR:user_data': None,
            'OS-EXT-STS:power_state': 1,
            'OS-EXT-STS:task_state': None,
            'OS-EXT-STS:vm_state': u'active',
            'OS-SCH-HNT:scheduler_hints': None,
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
            'block_device_mapping': None,
            'cloud': '_test_cloud_',
            'config_drive': u'True',
            'created': u'2015-08-01T19:52:16Z',
            'created_at': u'2015-08-01T19:52:16Z',
            'disk_config': u'MANUAL',
            'flavor': {u'id': u'bbcb7eb5-5c8d-498f-9d7e-307c575d3566'},
            'has_config_drive': True,
            'hostId': u'bd37',
            'host_id': u'bd37',
            'id': u'811c5197-dba7-4d3a-a3f6-68ca5328b9a7',
            'image': {u'id': u'69c99b45-cd53-49de-afdc-f24789eb8f83'},
            'instance_name': None,
            'interface_ip': '',
            'hypervisor_hostname': None,
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
            'personality': None,
            'power_state': 1,
            'private_v4': None,
            'progress': 0,
            'project_id': u'db92b20496ae4fbda850a689ea9d563f',
            'properties': {
                'OS-DCF:diskConfig': u'MANUAL',
                'OS-EXT-AZ:availability_zone': u'ca-ymq-2',
                'OS-EXT-SRV-ATTR:hypervisor_hostname': None,
                'OS-EXT-SRV-ATTR:instance_name': None,
                'OS-EXT-SRV-ATTR:user_data': None,
                'OS-EXT-STS:power_state': 1,
                'OS-EXT-STS:task_state': None,
                'OS-EXT-STS:vm_state': u'active',
                'OS-SCH-HNT:scheduler_hints': None,
                'OS-SRV-USG:launched_at': u'2015-08-01T19:52:02.000000',
                'OS-SRV-USG:terminated_at': None,
                'os-extended-volumes:volumes_attached': []},
            'public_v4': None,
            'public_v6': None,
            'region': u'RegionOne',
            'scheduler_hints': None,
            'security_groups': [{u'name': u'default'}],
            'status': u'ACTIVE',
            'tags': [],
            'task_state': None,
            'tenant_id': u'db92b20496ae4fbda850a689ea9d563f',
            'terminated_at': None,
            'updated': u'2016-10-15T15:49:29Z',
            'user_data': None,
            'user_id': u'e9b21dc437d149858faee0898fb08e92',
            'vm_state': u'active',
            'volumes': []}
        retval = self.cloud._normalize_server(res._to_munch())
        _assert_server_munch_attributes(self, res, retval)
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
                    domain_name='default',
                    id='1c36b64c840a42cd9e9b931a369337f0',
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
                             domain_name='default',
                             id='1c36b64c840a42cd9e9b931a369337f0',
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
                         domain_name='default',
                         id='1c36b64c840a42cd9e9b931a369337f0',
                         domain_id=None,
                         name='admin'),
                     cloud='_test_cloud_'))
        ]
        retval = self.cloud._normalize_secgroup_rules(nova_rules)
        self.assertEqual(expected, retval)

    def test_normalize_volumes_v1(self):
        vol = dict(
            id='55db9e89-9cb4-4202-af88-d8c4a174998e',
            display_name='test',
            display_description='description',
            bootable=u'false',   # unicode type
            multiattach='true',  # str type
            status='in-use',
            created_at='2015-08-27T09:49:58-05:00',
        )
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'block-storage', 'public', append=['volumes', 'detail']),
                 json={'volumes': [vol]}),
        ])
        expected = {
            'attachments': [],
            'availability_zone': None,
            'bootable': False,
            'can_multiattach': True,
            'consistencygroup_id': None,
            'created_at': vol['created_at'],
            'description': vol['display_description'],
            'display_description': vol['display_description'],
            'display_name': vol['display_name'],
            'encrypted': False,
            'host': None,
            'id': '55db9e89-9cb4-4202-af88-d8c4a174998e',
            'is_bootable': False,
            'is_encrypted': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': 'default',
                    'id': '1c36b64c840a42cd9e9b931a369337f0',
                    'name': 'admin'},
                'region_name': u'RegionOne',
                'zone': None},
            'metadata': {},
            'migration_status': None,
            'multiattach': True,
            'name': vol['display_name'],
            'properties': {},
            'replication_driver': None,
            'replication_extended_status': None,
            'replication_status': None,
            'size': 0,
            'snapshot_id': None,
            'source_volume_id': None,
            'status': vol['status'],
            'updated_at': None,
            'volume_type': None,
        }
        retval = self.cloud.list_volumes(vol)[0]
        self.assertEqual(expected, retval)

    def test_normalize_volumes_v2(self):
        vol = dict(
            id='55db9e89-9cb4-4202-af88-d8c4a174998e',
            name='test',
            description='description',
            bootable=False,
            multiattach=True,
            status='in-use',
            created_at='2015-08-27T09:49:58-05:00',
            availability_zone='my-zone',
        )
        vol['os-vol-tenant-attr:tenant_id'] = 'my-project'
        expected = {
            'attachments': [],
            'availability_zone': vol['availability_zone'],
            'bootable': False,
            'can_multiattach': True,
            'consistencygroup_id': None,
            'created_at': vol['created_at'],
            'description': vol['description'],
            'display_description': vol['description'],
            'display_name': vol['name'],
            'encrypted': False,
            'host': None,
            'id': '55db9e89-9cb4-4202-af88-d8c4a174998e',
            'is_bootable': False,
            'is_encrypted': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': None,
                    'id': vol['os-vol-tenant-attr:tenant_id'],
                    'name': None},
                'region_name': u'RegionOne',
                'zone': vol['availability_zone']},
            'metadata': {},
            'migration_status': None,
            'multiattach': True,
            'name': vol['name'],
            'os-vol-tenant-attr:tenant_id': vol[
                'os-vol-tenant-attr:tenant_id'],
            'properties': {
                'os-vol-tenant-attr:tenant_id': vol[
                    'os-vol-tenant-attr:tenant_id']},
            'replication_driver': None,
            'replication_extended_status': None,
            'replication_status': None,
            'size': 0,
            'snapshot_id': None,
            'source_volume_id': None,
            'status': vol['status'],
            'updated_at': None,
            'volume_type': None,
        }
        retval = self.cloud._normalize_volume(vol)
        self.assertEqual(expected, retval)


class TestStrictNormalize(base.TestCase):

    strict_cloud = True

    def setUp(self):
        super(TestStrictNormalize, self).setUp()
        self.assertTrue(self.cloud.strict_mode)

    def test_normalize_flavors(self):
        raw_flavor = RAW_FLAVOR_DICT.copy()
        expected = {
            'disk': 40,
            'ephemeral': 80,
            'extra_specs': {
                u'class': u'performance1',
                u'disk_io_index': u'40',
                u'number_of_data_disks': u'1',
                u'policy_class': u'performance_flavor',
                u'resize_policy_class': u'performance_flavor'},
            'id': u'performance1-8',
            'is_disabled': False,
            'is_public': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': 'default',
                    'id': u'1c36b64c840a42cd9e9b931a369337f0',
                    'name': 'admin'},
                'region_name': u'RegionOne',
                'zone': None},
            'name': u'8 GB Performance',
            'properties': {},
            'ram': 8192,
            'rxtx_factor': 1600.0,
            'swap': 0,
            'vcpus': 8}
        retval = self.cloud._normalize_flavor(raw_flavor)
        self.assertEqual(expected, retval)

    def test_normalize_nova_images(self):
        raw_image = RAW_NOVA_IMAGE_DICT.copy()
        expected = {
            'checksum': None,
            'container_format': None,
            'created_at': '2015-02-15T22:58:45Z',
            'direct_url': None,
            'disk_format': None,
            'file': None,
            'id': u'f2868d7c-63e1-4974-a64d-8670a86df21e',
            'is_protected': False,
            'is_public': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': 'default',
                    'id': u'1c36b64c840a42cd9e9b931a369337f0',
                    'name': 'admin'},
                'region_name': u'RegionOne',
                'zone': None},
            'locations': [],
            'min_disk': 20,
            'min_ram': 0,
            'name': u'Test Monty Ubuntu',
            'owner': None,
            'properties': {
                u'auto_disk_config': u'False',
                u'com.rackspace__1__build_core': u'1',
                u'com.rackspace__1__build_managed': u'1',
                u'com.rackspace__1__build_rackconnect': u'1',
                u'com.rackspace__1__options': u'0',
                u'com.rackspace__1__source': u'import',
                u'com.rackspace__1__visible_core': u'1',
                u'com.rackspace__1__visible_managed': u'1',
                u'com.rackspace__1__visible_rackconnect': u'1',
                u'image_type': u'import',
                u'org.openstack__1__architecture': u'x64',
                u'os_type': u'linux',
                u'user_id': u'156284',
                u'vm_mode': u'hvm',
                u'xenapi_use_agent': u'False',
                'OS-DCF:diskConfig': u'MANUAL',
                'progress': 100},
            'size': 323004185,
            'status': u'active',
            'tags': [],
            'updated_at': u'2015-02-15T23:04:34Z',
            'virtual_size': 0,
            'visibility': 'private'}
        retval = self.cloud._normalize_image(raw_image)
        self.assertEqual(sorted(expected.keys()), sorted(retval.keys()))
        self.assertEqual(expected, retval)

    def test_normalize_glance_images(self):
        raw_image = RAW_GLANCE_IMAGE_DICT.copy()
        expected = {
            'checksum': u'774f48af604ab1ec319093234c5c0019',
            'container_format': u'ovf',
            'created_at': u'2015-02-15T22:58:45Z',
            'direct_url': None,
            'disk_format': u'vhd',
            'file': u'/v2/images/f2868d7c-63e1-4974-a64d-8670a86df21e/file',
            'id': u'f2868d7c-63e1-4974-a64d-8670a86df21e',
            'is_protected': False,
            'is_public': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': None,
                    'id': u'610275',
                    'name': None},
                'region_name': u'RegionOne',
                'zone': None},
            'locations': [],
            'min_disk': 20,
            'min_ram': 0,
            'name': u'Test Monty Ubuntu',
            'owner': u'610275',
            'properties': {
                u'auto_disk_config': u'False',
                u'com.rackspace__1__build_core': u'1',
                u'com.rackspace__1__build_managed': u'1',
                u'com.rackspace__1__build_rackconnect': u'1',
                u'com.rackspace__1__options': u'0',
                u'com.rackspace__1__source': u'import',
                u'com.rackspace__1__visible_core': u'1',
                u'com.rackspace__1__visible_managed': u'1',
                u'com.rackspace__1__visible_rackconnect': u'1',
                u'image_type': u'import',
                u'org.openstack__1__architecture': u'x64',
                u'os_type': u'linux',
                u'schema': u'/v2/schemas/image',
                u'user_id': u'156284',
                u'vm_mode': u'hvm',
                u'xenapi_use_agent': u'False'},
            'size': 323004185,
            'status': u'active',
            'tags': [],
            'updated_at': u'2015-02-15T23:04:34Z',
            'virtual_size': 0,
            'visibility': 'private'}
        retval = self.cloud._normalize_image(raw_image)
        self.assertEqual(sorted(expected.keys()), sorted(retval.keys()))
        self.assertEqual(expected, retval)

    def test_normalize_servers(self):

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [RAW_SERVER_DICT]}),
        ])
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
            'block_device_mapping': None,
            'created': u'2015-08-01T19:52:16Z',
            'created_at': u'2015-08-01T19:52:16Z',
            'disk_config': u'MANUAL',
            'flavor': {u'id': u'bbcb7eb5-5c8d-498f-9d7e-307c575d3566'},
            'has_config_drive': True,
            'host_id': u'bd37',
            'hypervisor_hostname': None,
            'id': u'811c5197-dba7-4d3a-a3f6-68ca5328b9a7',
            'image': {u'id': u'69c99b45-cd53-49de-afdc-f24789eb8f83'},
            'interface_ip': u'',
            'instance_name': None,
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
            'personality': None,
            'power_state': 1,
            'private_v4': None,
            'progress': 0,
            'properties': {},
            'public_v4': None,
            'public_v6': None,
            'scheduler_hints': None,
            'security_groups': [{u'name': u'default'}],
            'status': u'ACTIVE',
            'tags': [],
            'task_state': None,
            'terminated_at': None,
            'updated': u'2016-10-15T15:49:29Z',
            'user_data': None,
            'user_id': u'e9b21dc437d149858faee0898fb08e92',
            'vm_state': u'active',
            'volumes': []}
        self.cloud.strict_mode = True
        retval = self.cloud.list_servers(bare=True)[0]
        _assert_server_munch_attributes(self, expected, retval)
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
            properties={},
            location=dict(
                region_name='RegionOne',
                zone=None,
                project=dict(
                    domain_name='default',
                    id='1c36b64c840a42cd9e9b931a369337f0',
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
                             domain_name='default',
                             id='1c36b64c840a42cd9e9b931a369337f0',
                             domain_id=None,
                             name='admin'),
                         cloud='_test_cloud_'))
            ]
        )

        retval = self.cloud._normalize_secgroup(nova_secgroup)
        self.assertEqual(expected, retval)

    def test_normalize_volumes_v1(self):
        vol = dict(
            id='55db9e89-9cb4-4202-af88-d8c4a174998e',
            display_name='test',
            display_description='description',
            bootable=u'false',   # unicode type
            multiattach='true',  # str type
            status='in-use',
            created_at='2015-08-27T09:49:58-05:00',
        )
        expected = {
            'attachments': [],
            'can_multiattach': True,
            'consistencygroup_id': None,
            'created_at': vol['created_at'],
            'description': vol['display_description'],
            'host': None,
            'id': '55db9e89-9cb4-4202-af88-d8c4a174998e',
            'is_bootable': False,
            'is_encrypted': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': 'default',
                    'id': '1c36b64c840a42cd9e9b931a369337f0',
                    'name': 'admin'},
                'region_name': u'RegionOne',
                'zone': None},
            'metadata': {},
            'migration_status': None,
            'name': vol['display_name'],
            'properties': {},
            'replication_driver': None,
            'replication_extended_status': None,
            'replication_status': None,
            'size': 0,
            'snapshot_id': None,
            'source_volume_id': None,
            'status': vol['status'],
            'updated_at': None,
            'volume_type': None,
        }
        retval = self.cloud._normalize_volume(vol)
        self.assertEqual(expected, retval)

    def test_normalize_volumes_v2(self):
        vol = dict(
            id='55db9e89-9cb4-4202-af88-d8c4a174998e',
            name='test',
            description='description',
            bootable=False,
            multiattach=True,
            status='in-use',
            created_at='2015-08-27T09:49:58-05:00',
            availability_zone='my-zone',
        )
        vol['os-vol-tenant-attr:tenant_id'] = 'my-project'
        expected = {
            'attachments': [],
            'can_multiattach': True,
            'consistencygroup_id': None,
            'created_at': vol['created_at'],
            'description': vol['description'],
            'host': None,
            'id': '55db9e89-9cb4-4202-af88-d8c4a174998e',
            'is_bootable': False,
            'is_encrypted': False,
            'location': {
                'cloud': '_test_cloud_',
                'project': {
                    'domain_id': None,
                    'domain_name': None,
                    'id': vol['os-vol-tenant-attr:tenant_id'],
                    'name': None},
                'region_name': u'RegionOne',
                'zone': vol['availability_zone']},
            'metadata': {},
            'migration_status': None,
            'name': vol['name'],
            'properties': {},
            'replication_driver': None,
            'replication_extended_status': None,
            'replication_status': None,
            'size': 0,
            'snapshot_id': None,
            'source_volume_id': None,
            'status': vol['status'],
            'updated_at': None,
            'volume_type': None,
        }
        retval = self.cloud._normalize_volume(vol)
        self.assertEqual(expected, retval)
