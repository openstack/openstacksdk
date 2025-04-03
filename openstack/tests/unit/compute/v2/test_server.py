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

import http
from unittest import mock

from openstack.compute.v2 import flavor
from openstack.compute.v2 import server
from openstack.image.v2 import image
from openstack.tests.unit import base
from openstack.tests.unit import fakes

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'OS-DCF:diskConfig': 'AUTO',
    'OS-EXT-AZ:availability_zone': 'us-west',
    'OS-EXT-SRV-ATTR:host': 'compute',
    'OS-EXT-SRV-ATTR:hostname': 'new-server-test',
    'OS-EXT-SRV-ATTR:hypervisor_hostname': 'fake-mini',
    'OS-EXT-SRV-ATTR:instance_name': 'instance-00000001',
    'OS-EXT-SRV-ATTR:kernel_id': '',
    'OS-EXT-SRV-ATTR:launch_index': 0,
    'OS-EXT-SRV-ATTR:ramdisk_id': '',
    'OS-EXT-SRV-ATTR:reservation_id': 'r-ov3q80zj',
    'OS-EXT-SRV-ATTR:root_device_name': '/dev/sda',
    'OS-EXT-SRV-ATTR:user_data': 'IyEvYmluL2Jhc2gKL2Jpbi9IHlvdSEiCg==',
    'OS-EXT-STS:power_state': 1,
    'OS-EXT-STS:task_state': None,
    'OS-EXT-STS:vm_state': 'active',
    'OS-SRV-USG:launched_at': '2017-02-14T19:23:59.895661',
    'OS-SRV-USG:terminated_at': '2015-03-09T12:15:57.233772',
    'OS-SCH-HNT:scheduler_hints': {'key': '30'},
    'accessIPv4': '1.2.3.4',
    'accessIPv6': '80fe::',
    'adminPass': '27',
    'addresses': {
        'private': [
            {
                'OS-EXT-IPS-MAC:mac_addr': 'aa:bb:cc:dd:ee:ff',
                'OS-EXT-IPS:type': 'fixed',
                'addr': '192.168.0.3',
                'version': 4,
            }
        ]
    },
    'block_device_mapping_v2': {'key': '29'},
    'config_drive': '',
    'created': '2017-02-14T19:23:58Z',
    'description': 'dummy',
    'flavorRef': '5',
    'flavor': {
        'disk': 1,
        'ephemeral': 0,
        'extra_specs': {
            'hw:cpu_policy': 'dedicated',
            'hw:mem_page_size': '2048',
        },
        'original_name': 'm1.tiny.specs',
        'ram': 512,
        'swap': 0,
    },
    'hostId': '2091634baaccdc4c5a1d57069c833e402921df696b7f970791b12ec6',
    'host_status': 'UP',
    'id': IDENTIFIER,
    'imageRef': '8',
    'image': {
        'id': '70a599e0-31e7-49b7-b260-868f441e862b',
        'links': [
            {
                'href': 'http://openstack.example.com/images/70a599e0',
                'rel': 'bookmark',
            }
        ],
    },
    'key_name': 'dummy',
    'links': [
        {
            'href': 'http://openstack.example.com/v2.1/servers/9168b536',
            'rel': 'self',
        },
        {
            'href': 'http://openstack.example.com/servers/9168b536',
            'rel': 'bookmark',
        },
    ],
    'locked': True,
    'metadata': {'My Server Name': 'Apache1'},
    'name': 'new-server-test',
    'networks': 'auto',
    'os-extended-volumes:volumes_attached': [],
    'progress': 0,
    'security_groups': [{'name': 'default'}],
    'server_groups': ['3caf4187-8010-491f-b6f5-a4a68a40371e'],
    'status': 'ACTIVE',
    'tags': [],
    'tenant_id': '6f70656e737461636b20342065766572',
    'trusted_image_certificates': [
        '0b5d2c72-12cc-4ba6-a8d7-3ff5cc1d8cb8',
        '674736e3-f25c-405c-8362-bbf991e0ce0a',
    ],
    'updated': '2017-02-14T19:24:00Z',
    'user_id': 'fake',
}


class TestServer(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.sess = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)
        # totally arbitrary
        self.sess.default_microversion = '2.88'

    def test_basic(self):
        sot = server.Server()
        self.assertEqual('server', sot.resource_key)
        self.assertEqual('servers', sot.resources_key)
        self.assertEqual('/servers', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                "access_ipv4": "access_ip_v4",
                "access_ipv6": "access_ip_v6",
                "auto_disk_config": "auto_disk_config",
                "availability_zone": "availability_zone",
                "changes_before": "changes-before",
                "changes_since": "changes-since",
                "compute_host": "host",
                "has_config_drive": "config_drive",
                "created_at": "created_at",
                "description": "description",
                "flavor": "flavor",
                "hostname": "hostname",
                "image": "image",
                "ipv4_address": "ip",
                "ipv6_address": "ip6",
                "id": "uuid",
                "deleted_only": "deleted",
                "is_soft_deleted": "soft_deleted",
                "kernel_id": "kernel_id",
                "key_name": "key_name",
                "launch_index": "launch_index",
                "launched_at": "launched_at",
                "limit": "limit",
                "locked": "locked",
                "locked_by": "locked_by",
                "marker": "marker",
                "name": "name",
                "node": "node",
                "power_state": "power_state",
                "progress": "progress",
                "project_id": "project_id",
                "ramdisk_id": "ramdisk_id",
                "pinned_availability_zone": "pinned_availability_zone",
                "reservation_id": "reservation_id",
                "root_device_name": "root_device_name",
                "sort_dir": "sort_dir",
                "sort_key": "sort_key",
                "status": "status",
                "task_state": "task_state",
                "terminated_at": "terminated_at",
                "user_id": "user_id",
                "vm_state": "vm_state",
                "all_projects": "all_tenants",
                "tags": "tags",
                "any_tags": "tags-any",
                "not_tags": "not-tags",
                "not_any_tags": "not-tags-any",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = server.Server(**EXAMPLE)
        self.assertEqual(EXAMPLE['accessIPv4'], sot.access_ipv4)
        self.assertEqual(EXAMPLE['accessIPv6'], sot.access_ipv6)
        self.assertEqual(EXAMPLE['addresses'], sot.addresses)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['config_drive'], sot.has_config_drive)
        self.assertEqual(EXAMPLE['flavorRef'], sot.flavor_id)
        self.assertEqual(flavor.Flavor(**EXAMPLE['flavor']), sot.flavor)
        self.assertEqual(EXAMPLE['hostId'], sot.host_id)
        self.assertEqual(EXAMPLE['host_status'], sot.host_status)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['imageRef'], sot.image_id)
        self.assertEqual(image.Image(**EXAMPLE['image']), sot.image)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['networks'], sot.networks)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['progress'], sot.progress)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['server_groups'], sot.server_groups)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
        self.assertEqual(EXAMPLE['key_name'], sot.key_name)
        self.assertEqual(EXAMPLE['OS-DCF:diskConfig'], sot.disk_config)
        self.assertEqual(
            EXAMPLE['OS-EXT-AZ:availability_zone'], sot.availability_zone
        )
        self.assertEqual(EXAMPLE['OS-EXT-STS:power_state'], sot.power_state)
        self.assertEqual(EXAMPLE['OS-EXT-STS:task_state'], sot.task_state)
        self.assertEqual(EXAMPLE['OS-EXT-STS:vm_state'], sot.vm_state)
        self.assertEqual(
            EXAMPLE['os-extended-volumes:volumes_attached'],
            sot.attached_volumes,
        )
        self.assertEqual(EXAMPLE['OS-SRV-USG:launched_at'], sot.launched_at)
        self.assertEqual(
            EXAMPLE['OS-SRV-USG:terminated_at'], sot.terminated_at
        )
        self.assertEqual(EXAMPLE['security_groups'], sot.security_groups)
        self.assertEqual(EXAMPLE['adminPass'], sot.admin_password)
        self.assertEqual(
            EXAMPLE['block_device_mapping_v2'], sot.block_device_mapping
        )
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:host'], sot.compute_host)
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:hostname'], sot.hostname)
        self.assertEqual(
            EXAMPLE['OS-EXT-SRV-ATTR:hypervisor_hostname'],
            sot.hypervisor_hostname,
        )
        self.assertEqual(
            EXAMPLE['OS-EXT-SRV-ATTR:instance_name'], sot.instance_name
        )
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:kernel_id'], sot.kernel_id)
        self.assertEqual(
            EXAMPLE['OS-EXT-SRV-ATTR:launch_index'], sot.launch_index
        )
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:ramdisk_id'], sot.ramdisk_id)
        self.assertEqual(
            EXAMPLE['OS-EXT-SRV-ATTR:reservation_id'], sot.reservation_id
        )
        self.assertEqual(
            EXAMPLE['OS-EXT-SRV-ATTR:root_device_name'], sot.root_device_name
        )
        self.assertEqual(
            EXAMPLE['OS-SCH-HNT:scheduler_hints'], sot.scheduler_hints
        )
        self.assertEqual(EXAMPLE['OS-EXT-SRV-ATTR:user_data'], sot.user_data)
        self.assertEqual(EXAMPLE['locked'], sot.is_locked)
        self.assertEqual(
            EXAMPLE['trusted_image_certificates'],
            sot.trusted_image_certificates,
        )

    def test_to_dict_flavor(self):
        # Ensure to_dict properly resolves flavor and uses defaults for not
        # specified flavor proerties.
        sot = server.Server(**EXAMPLE)
        dct = sot.to_dict()
        self.assertEqual(0, dct['flavor']['vcpus'])

    def test__prepare_server(self):
        zone = 1
        data = 2
        hints = {"hint": 3}

        sot = server.Server(
            id=1,
            availability_zone=zone,
            user_data=data,
            scheduler_hints=hints,
            min_count=2,
            max_count=3,
        )
        request = sot._prepare_request()

        self.assertNotIn(
            "OS-EXT-AZ:availability_zone", request.body[sot.resource_key]
        )
        self.assertEqual(
            request.body[sot.resource_key]["availability_zone"], zone
        )

        self.assertNotIn(
            "OS-EXT-SRV-ATTR:user_data", request.body[sot.resource_key]
        )
        self.assertEqual(request.body[sot.resource_key]["user_data"], data)

        self.assertNotIn(
            "OS-SCH-HNT:scheduler_hints", request.body[sot.resource_key]
        )
        self.assertEqual(request.body["OS-SCH-HNT:scheduler_hints"], hints)

        self.assertEqual(2, request.body[sot.resource_key]['min_count'])
        self.assertEqual(3, request.body[sot.resource_key]['max_count'])

    def test_change_password(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.change_password(self.sess, 'a'))

        url = 'servers/IDENTIFIER/action'
        body = {"changePassword": {"adminPass": "a"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_get_password(self):
        sot = server.Server(**EXAMPLE)
        self.sess.get.return_value = fakes.FakeResponse(
            data={'password': 'foo'}
        )

        result = sot.get_password(self.sess)
        self.assertEqual('foo', result)

        url = 'servers/IDENTIFIER/os-server-password'
        self.sess.get.assert_called_with(
            url, microversion=self.sess.default_microversion
        )

    def test_clear_password(self):
        sot = server.Server(**EXAMPLE)
        self.sess.delete.return_value = fakes.FakeResponse(
            status_code=http.HTTPStatus.NO_CONTENT,
        )

        self.assertIsNone(sot.clear_password(self.sess))

        url = 'servers/IDENTIFIER/os-server-password'
        self.sess.delete.assert_called_with(
            url, microversion=self.sess.default_microversion
        )

    def test_reboot(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.reboot(self.sess, 'HARD'))

        url = 'servers/IDENTIFIER/action'
        body = {"reboot": {"type": "HARD"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_force_delete(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.force_delete(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {'forceDelete': None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_rebuild(self):
        sot = server.Server(**EXAMPLE)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = lambda arg: arg

        result = sot.rebuild(
            self.sess,
            '123',
            name='noo',
            admin_password='seekr3t',
            preserve_ephemeral=False,
            access_ipv4="12.34.56.78",
            access_ipv6="fe80::100",
            metadata={"meta var": "meta val"},
            user_data="ZWNobyAiaGVsbG8gd29ybGQi",
            key_name='my-ecdsa-key',
            description='an updated description',
            trusted_image_certificates=['foo'],
            hostname='new-hostname',
        )

        self.assertIsInstance(result, server.Server)

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "name": "noo",
                "imageRef": "123",
                "adminPass": "seekr3t",
                "accessIPv4": "12.34.56.78",
                "accessIPv6": "fe80::100",
                "metadata": {"meta var": "meta val"},
                "user_data": "ZWNobyAiaGVsbG8gd29ybGQi",
                "preserve_ephemeral": False,
                "key_name": 'my-ecdsa-key',
                "description": 'an updated description',
                "trusted_image_certificates": ['foo'],
                "hostname": "new-hostname",
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_rebuild_minimal(self):
        sot = server.Server(**EXAMPLE)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = lambda arg: arg

        result = sot.rebuild(
            self.sess,
            '123',
            name='nootoo',
            admin_password='seekr3two',
        )

        self.assertIsInstance(result, server.Server)

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "name": "nootoo",
                "imageRef": "123",
                "adminPass": "seekr3two",
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_rebuild_none_values(self):
        sot = server.Server(**EXAMPLE)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = lambda arg: arg

        result = sot.rebuild(
            self.sess,
            '123',
            admin_password=None,
            access_ipv4=None,
            access_ipv6=None,
            metadata=None,
            user_data=None,
            description=None,
        )

        self.assertIsInstance(result, server.Server)

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "imageRef": "123",
                "adminPass": None,
                "accessIPv4": None,
                "accessIPv6": None,
                "metadata": None,
                "user_data": None,
                "description": None,
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.resize(self.sess, '2'))

        url = 'servers/IDENTIFIER/action'
        body = {"resize": {"flavorRef": "2"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_confirm_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.confirm_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"confirmResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_revert_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.revert_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"revertResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_shelve_offload(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.shelve_offload(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"shelveOffload": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_create_image_header(self):
        sot = server.Server(**EXAMPLE)
        name = 'noo'
        metadata = {'nu': 'image', 'created': 'today'}

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name, 'metadata': metadata}}
        headers = {'Accept': ''}

        rsp = mock.Mock()
        rsp.json.return_value = None
        rsp.headers = {'Location': 'dummy/dummy2'}
        rsp.status_code = 200

        self.sess.post.return_value = rsp

        self.endpoint_data = mock.Mock(
            spec=['min_microversion', 'max_microversion'],
            min_microversion=None,
            max_microversion='2.44',
        )
        self.sess.get_endpoint_data.return_value = self.endpoint_data

        image_id = sot.create_image(self.sess, name, metadata)

        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

        self.assertEqual('dummy2', image_id)

    def test_create_image_microver(self):
        sot = server.Server(**EXAMPLE)
        name = 'noo'
        metadata = {'nu': 'image', 'created': 'today'}

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name, 'metadata': metadata}}
        headers = {'Accept': ''}

        rsp = mock.Mock()
        rsp.json.return_value = {'image_id': 'dummy3'}
        rsp.headers = {'Location': 'dummy/dummy2'}
        rsp.status_code = 200

        self.sess.post.return_value = rsp

        self.endpoint_data = mock.Mock(
            spec=['min_microversion', 'max_microversion'],
            min_microversion='2.1',
            max_microversion='2.56',
        )
        self.sess.get_endpoint_data.return_value = self.endpoint_data
        self.sess.default_microversion = None

        image_id = sot.create_image(self.sess, name, metadata)

        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion='2.45'
        )

        self.assertEqual('dummy3', image_id)

    def test_create_image_minimal(self):
        sot = server.Server(**EXAMPLE)
        name = 'noo'
        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name}}
        headers = {'Accept': ''}

        rsp = mock.Mock()
        rsp.json.return_value = None
        rsp.headers = {'Location': 'dummy/dummy2'}
        rsp.status_code = 200

        self.sess.post.return_value = rsp

        self.endpoint_data = mock.Mock(
            spec=['min_microversion', 'max_microversion'],
            min_microversion='2.1',
            max_microversion='2.56',
        )
        self.sess.get_endpoint_data.return_value = self.endpoint_data
        self.sess.default_microversion = None

        self.assertIsNone(self.resp.body, sot.create_image(self.sess, name))

        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion='2.45'
        )

    def test_add_security_group(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.add_security_group(self.sess, "group"))

        url = 'servers/IDENTIFIER/action'
        body = {"addSecurityGroup": {"name": "group"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_remove_security_group(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.remove_security_group(self.sess, "group"))

        url = 'servers/IDENTIFIER/action'
        body = {"removeSecurityGroup": {"name": "group"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_reset_state(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.reset_state(self.sess, 'active'))

        url = 'servers/IDENTIFIER/action'
        body = {"os-resetState": {"state": 'active'}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_add_fixed_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.add_fixed_ip(self.sess, "NETWORK-ID")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"addFixedIp": {"networkId": "NETWORK-ID"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_remove_fixed_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.remove_fixed_ip(self.sess, "ADDRESS")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"removeFixedIp": {"address": "ADDRESS"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_add_floating_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.add_floating_ip(self.sess, "FLOATING-IP")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"addFloatingIp": {"address": "FLOATING-IP"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_add_floating_ip_with_fixed_addr(self):
        sot = server.Server(**EXAMPLE)

        res = sot.add_floating_ip(self.sess, "FLOATING-IP", "FIXED-ADDR")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "addFloatingIp": {
                "address": "FLOATING-IP",
                "fixed_address": "FIXED-ADDR",
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_remove_floating_ip(self):
        sot = server.Server(**EXAMPLE)

        res = sot.remove_floating_ip(self.sess, "I-AM-FLOATING")

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"removeFloatingIp": {"address": "I-AM-FLOATING"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_backup(self):
        sot = server.Server(**EXAMPLE)

        res = sot.backup(self.sess, "name", "daily", 1)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "createBackup": {
                "name": "name",
                "backup_type": "daily",
                "rotation": 1,
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_pause(self):
        sot = server.Server(**EXAMPLE)

        res = sot.pause(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"pause": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unpause(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unpause(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unpause": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_suspend(self):
        sot = server.Server(**EXAMPLE)

        res = sot.suspend(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"suspend": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_resume(self):
        sot = server.Server(**EXAMPLE)

        res = sot.resume(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"resume": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_lock(self):
        sot = server.Server(**EXAMPLE)

        res = sot.lock(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"lock": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_lock_with_options(self):
        sot = server.Server(**EXAMPLE)

        res = sot.lock(self.sess, locked_reason='Because why not')

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'lock': {'locked_reason': 'Because why not'}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unlock(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unlock(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unlock": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_rescue(self):
        sot = server.Server(**EXAMPLE)

        res = sot.rescue(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"rescue": {}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_rescue_with_options(self):
        sot = server.Server(**EXAMPLE)

        res = sot.rescue(self.sess, admin_pass='SECRET', image_ref='IMG-ID')

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "rescue": {'adminPass': 'SECRET', 'rescue_image_ref': 'IMG-ID'}
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unrescue(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unrescue(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unrescue": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_evacuate(self):
        sot = server.Server(**EXAMPLE)

        res = sot.evacuate(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"evacuate": {}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_evacuate_with_options(self):
        sot = server.Server(**EXAMPLE)

        res = sot.evacuate(
            self.sess,
            host='HOST2',
            admin_pass='NEW_PASS',
            force=True,
            on_shared_storage=False,
        )

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "evacuate": {
                'host': 'HOST2',
                'adminPass': 'NEW_PASS',
                'force': True,
                'onSharedStorage': False,
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_start(self):
        sot = server.Server(**EXAMPLE)

        res = sot.start(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"os-start": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_stop(self):
        sot = server.Server(**EXAMPLE)

        res = sot.stop(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"os-stop": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_restore(self):
        sot = server.Server(**EXAMPLE)

        res = sot.restore(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'restore': None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_shelve(self):
        sot = server.Server(**EXAMPLE)

        res = sot.shelve(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"shelve": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unshelve(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unshelve(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unshelve": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unshelve_availability_zone(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unshelve(self.sess, sot.availability_zone)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unshelve": {"availability_zone": sot.availability_zone}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unshelve_unpin_az(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unshelve(self.sess, availability_zone=None)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unshelve": {"availability_zone": None}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unshelve_host(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unshelve(self.sess, host=sot.hypervisor_hostname)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"unshelve": {"host": sot.hypervisor_hostname}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_unshelve_host_and_availability_zone(self):
        sot = server.Server(**EXAMPLE)

        res = sot.unshelve(
            self.sess,
            availability_zone=sot.availability_zone,
            host=sot.hypervisor_hostname,
        )

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "unshelve": {
                "availability_zone": sot.availability_zone,
                "host": sot.hypervisor_hostname,
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_migrate(self):
        sot = server.Server(**EXAMPLE)

        res = sot.migrate(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {"migrate": None}

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_trigger_crash_dump(self):
        sot = server.Server(**EXAMPLE)

        res = sot.trigger_crash_dump(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'trigger_crash_dump': None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_get_console_output(self):
        sot = server.Server(**EXAMPLE)

        res = sot.get_console_output(self.sess)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'os-getConsoleOutput': {}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

        res = sot.get_console_output(self.sess, length=1)

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'os-getConsoleOutput': {'length': 1}}

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_get_console_url(self):
        sot = server.Server(**EXAMPLE)

        resp = mock.Mock()
        resp.body = {'console': {'a': 'b'}}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.post.return_value = resp

        res = sot.get_console_url(self.sess, 'novnc')
        self.sess.post.assert_called_with(
            'servers/IDENTIFIER/action',
            json={'os-getVNCConsole': {'type': 'novnc'}},
            headers={'Accept': ''},
            microversion=self.sess.default_microversion,
        )
        self.assertDictEqual(resp.body['console'], res)

        sot.get_console_url(self.sess, 'xvpvnc')
        self.sess.post.assert_called_with(
            'servers/IDENTIFIER/action',
            json={'os-getVNCConsole': {'type': 'xvpvnc'}},
            headers={'Accept': ''},
            microversion=self.sess.default_microversion,
        )

        sot.get_console_url(self.sess, 'spice-html5')
        self.sess.post.assert_called_with(
            'servers/IDENTIFIER/action',
            json={'os-getSPICEConsole': {'type': 'spice-html5'}},
            headers={'Accept': ''},
            microversion=self.sess.default_microversion,
        )

        sot.get_console_url(self.sess, 'spice-direct')
        self.sess.post.assert_called_with(
            'servers/IDENTIFIER/action',
            json={'os-getSPICEConsole': {'type': 'spice-direct'}},
            headers={'Accept': ''},
            microversion=self.sess.default_microversion,
        )

        sot.get_console_url(self.sess, 'rdp-html5')
        self.sess.post.assert_called_with(
            'servers/IDENTIFIER/action',
            json={'os-getRDPConsole': {'type': 'rdp-html5'}},
            headers={'Accept': ''},
            microversion=self.sess.default_microversion,
        )

        sot.get_console_url(self.sess, 'serial')
        self.sess.post.assert_called_with(
            'servers/IDENTIFIER/action',
            json={'os-getSerialConsole': {'type': 'serial'}},
            headers={'Accept': ''},
            microversion=self.sess.default_microversion,
        )

        self.assertRaises(
            ValueError, sot.get_console_url, self.sess, 'fake_type'
        )

    def test_live_migrate_no_force(self):
        sot = server.Server(**EXAMPLE)

        class FakeEndpointData:
            min_microversion = None
            max_microversion = None

        self.sess.get_endpoint_data.return_value = FakeEndpointData()

        ex = self.assertRaises(
            ValueError,
            sot.live_migrate,
            self.sess,
            host='HOST2',
            force=False,
            block_migration=False,
        )
        self.assertIn("Live migration on this cloud implies 'force'", str(ex))

    def test_live_migrate_no_microversion_force_true(self):
        sot = server.Server(**EXAMPLE)

        class FakeEndpointData:
            min_microversion = None
            max_microversion = None

        self.sess.get_endpoint_data.return_value = FakeEndpointData()

        res = sot.live_migrate(
            self.sess,
            host='HOST2',
            force=True,
            block_migration=True,
            disk_over_commit=True,
        )

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            'os-migrateLive': {
                'host': 'HOST2',
                'disk_over_commit': True,
                'block_migration': True,
            }
        }

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url,
            json=body,
            headers=headers,
            microversion=self.sess.default_microversion,
        )

    def test_live_migrate_25(self):
        sot = server.Server(**EXAMPLE)

        class FakeEndpointData:
            min_microversion = '2.1'
            max_microversion = '2.25'

        self.sess.get_endpoint_data.return_value = FakeEndpointData()
        self.sess.default_microversion = None

        res = sot.live_migrate(
            self.sess, host='HOST2', force=True, block_migration=False
        )

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "os-migrateLive": {
                'block_migration': False,
                'host': 'HOST2',
            }
        }

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion='2.25'
        )

    def test_live_migrate_25_default_block(self):
        sot = server.Server(**EXAMPLE)

        class FakeEndpointData:
            min_microversion = '2.1'
            max_microversion = '2.25'

        self.sess.get_endpoint_data.return_value = FakeEndpointData()
        self.sess.default_microversion = None

        res = sot.live_migrate(
            self.sess, host='HOST2', force=True, block_migration=None
        )

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            "os-migrateLive": {
                'block_migration': 'auto',
                'host': 'HOST2',
            }
        }

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion='2.25'
        )

    def test_live_migrate_30(self):
        sot = server.Server(**EXAMPLE)

        class FakeEndpointData:
            min_microversion = '2.1'
            max_microversion = '2.30'

        self.sess.get_endpoint_data.return_value = FakeEndpointData()
        self.sess.default_microversion = None

        res = sot.live_migrate(
            self.sess, host='HOST2', force=False, block_migration=False
        )

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {'os-migrateLive': {'block_migration': False, 'host': 'HOST2'}}

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion='2.30'
        )

    def test_live_migrate_30_force(self):
        sot = server.Server(**EXAMPLE)

        class FakeEndpointData:
            min_microversion = '2.1'
            max_microversion = '2.30'

        self.sess.get_endpoint_data.return_value = FakeEndpointData()
        self.sess.default_microversion = None

        res = sot.live_migrate(
            self.sess, host='HOST2', force=True, block_migration=None
        )

        self.assertIsNone(res)
        url = 'servers/IDENTIFIER/action'
        body = {
            'os-migrateLive': {
                'block_migration': 'auto',
                'host': 'HOST2',
                'force': True,
            }
        }

        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion='2.30'
        )

    def test_get_topology(self):
        sot = server.Server(**EXAMPLE)

        class FakeEndpointData:
            min_microversion = '2.1'
            max_microversion = '2.78'

        self.sess.get_endpoint_data.return_value = FakeEndpointData()
        self.sess.default_microversion = None

        response = mock.Mock()

        topology = {
            "nodes": [
                {
                    "cpu_pinning": {"0": 0, "1": 5},
                    "host_node": 0,
                    "memory_mb": 1024,
                    "siblings": [[0, 1]],
                    "vcpu_set": [0, 1],
                },
                {
                    "cpu_pinning": {"2": 1, "3": 8},
                    "host_node": 1,
                    "memory_mb": 2048,
                    "siblings": [[2, 3]],
                    "vcpu_set": [2, 3],
                },
            ],
            "pagesize_kb": 4,
        }

        response.status_code = 200
        response.json.return_value = topology

        self.sess.get.return_value = response

        fetched_topology = sot.fetch_topology(self.sess)

        url = 'servers/IDENTIFIER/topology'
        self.sess.get.assert_called_with(url)

        self.assertEqual(fetched_topology, topology)

    def test_get_security_groups(self):
        sot = server.Server(**EXAMPLE)

        response = mock.Mock()

        sgs = [
            {
                'description': 'default',
                'id': 1,
                'name': 'default',
                'rules': [
                    {
                        'direction': 'egress',
                        'ethertype': 'IPv6',
                        'id': '3c0e45ff-adaf-4124-b083-bf390e5482ff',
                        'port_range_max': None,
                        'port_range_min': None,
                        'protocol': None,
                        'remote_group_id': None,
                        'remote_ip_prefix': None,
                        'security_group_id': '1',
                        'project_id': 'e4f50856753b4dc6afee5fa6b9b6c550',
                        'revision_number': 1,
                        'tags': ['tag1,tag2'],
                        'tenant_id': 'e4f50856753b4dc6afee5fa6b9b6c550',
                        'created_at': '2018-03-19T19:16:56Z',
                        'updated_at': '2018-03-19T19:16:56Z',
                        'description': '',
                    }
                ],
                'tenant_id': 'e4f50856753b4dc6afee5fa6b9b6c550',
            }
        ]

        response.status_code = 200
        response.json.return_value = {'security_groups': sgs}
        self.sess.get.return_value = response

        sot.fetch_security_groups(self.sess)

        url = 'servers/IDENTIFIER/os-security-groups'
        self.sess.get.assert_called_with(url)

        self.assertEqual(sot.security_groups, sgs)
