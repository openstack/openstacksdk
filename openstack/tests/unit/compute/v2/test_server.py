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

from openstack.compute.v2 import server

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'accessIPv4': '1',
    'accessIPv6': '2',
    'addresses': {'region': '3'},
    'created': '2015-03-09T12:14:57.233772',
    'flavorRef': '5',
    'hostId': '6',
    'id': IDENTIFIER,
    'imageRef': '8',
    'links': '9',
    'metadata': {'key': '10'},
    'name': '11',
    'progress': 12,
    'tenant_id': '13',
    'status': '14',
    'updated': '2015-03-09T12:15:57.233772',
    'user_id': '16',
    'key_name': '17',
    'OS-DCF:diskConfig': '18',
    'OS-EXT-AZ:availability_zone': '19',
    'OS-EXT-STS:power_state': '20',
    'OS-EXT-STS:task_state': '21',
    'OS-EXT-STS:vm_state': '22',
    'os-extended-volumes:volumes_attached': '23',
    'OS-SRV-USG:launched_at': '2015-03-09T12:15:57.233772',
    'OS-SRV-USG:terminated_at': '2015-03-09T12:15:57.233772',
    'security_groups': '26',
    'adminPass': '27',
    'personality': '28',
    'block_device_mapping_v2': {'key': '29'},
    'os:scheduler_hints': {'key': '30'},
    'user_data': '31'
}


class TestServer(testtools.TestCase):

    def setUp(self):
        super(TestServer, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = server.Server()
        self.assertEqual('server', sot.resource_key)
        self.assertEqual('servers', sot.resources_key)
        self.assertEqual('/servers', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({"image": "image",
                              "flavor": "flavor",
                              "name": "name",
                              "status": "status",
                              "host": "host",
                              "changes_since": "changes-since"},
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = server.Server(**EXAMPLE)
        self.assertEqual(EXAMPLE['accessIPv4'], sot.access_ipv4)
        self.assertEqual(EXAMPLE['accessIPv6'], sot.access_ipv6)
        self.assertEqual(EXAMPLE['addresses'], sot.addresses)
        self.assertEqual(EXAMPLE['created'], sot.created_at)
        self.assertEqual(EXAMPLE['flavorRef'], sot.flavor_id)
        self.assertEqual(EXAMPLE['hostId'], sot.host_id)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['imageRef'], sot.image_id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['progress'], sot.progress)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
        self.assertEqual(EXAMPLE['key_name'], sot.key_name)
        self.assertEqual(EXAMPLE['OS-DCF:diskConfig'], sot.disk_config)
        self.assertEqual(EXAMPLE['OS-EXT-AZ:availability_zone'],
                         sot.availability_zone)
        self.assertEqual(EXAMPLE['OS-EXT-STS:power_state'], sot.power_state)
        self.assertEqual(EXAMPLE['OS-EXT-STS:task_state'], sot.task_state)
        self.assertEqual(EXAMPLE['OS-EXT-STS:vm_state'], sot.vm_state)
        self.assertEqual(EXAMPLE['os-extended-volumes:volumes_attached'],
                         sot.attached_volumes)
        self.assertEqual(EXAMPLE['OS-SRV-USG:launched_at'], sot.launched_at)
        self.assertEqual(EXAMPLE['OS-SRV-USG:terminated_at'],
                         sot.terminated_at)
        self.assertEqual(EXAMPLE['security_groups'], sot.security_groups)
        self.assertEqual(EXAMPLE['adminPass'], sot.admin_password)
        self.assertEqual(EXAMPLE['personality'], sot.personality)
        self.assertEqual(EXAMPLE['block_device_mapping_v2'],
                         sot.block_device_mapping)
        self.assertEqual(EXAMPLE['os:scheduler_hints'], sot.scheduler_hints)
        self.assertEqual(EXAMPLE['user_data'], sot.user_data)

    def test_detail(self):
        sot = server.ServerDetail()
        self.assertEqual('server', sot.resource_key)
        self.assertEqual('servers', sot.resources_key)
        self.assertEqual('/servers/detail', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_change_passowrd(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.change_password(self.sess, 'a'))

        url = 'servers/IDENTIFIER/action'
        body = {"changePassword": {"adminPass": "a"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_reboot(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.reboot(self.sess, 'HARD'))

        url = 'servers/IDENTIFIER/action'
        body = {"reboot": {"type": "HARD"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_rebuild(self):
        sot = server.Server(**EXAMPLE)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = lambda arg: arg

        result = sot.rebuild(self.sess, name='noo', admin_password='seekr3t',
                             image='http://image/1', access_ipv4="12.34.56.78",
                             access_ipv6="fe80::100",
                             metadata={"meta var": "meta val"},
                             personality=[{"path": "/etc/motd",
                                           "contents": "foo"}])

        self.assertIsInstance(result, server.Server)

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "name": "noo",
                "imageRef": "http://image/1",
                "adminPass": "seekr3t",
                "accessIPv4": "12.34.56.78",
                "accessIPv6": "fe80::100",
                "metadata": {"meta var": "meta val"},
                "personality": [{"path": "/etc/motd", "contents": "foo"}],
                "preserve_ephemeral": False
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_rebuild_minimal(self):
        sot = server.Server(**EXAMPLE)
        # Let the translate pass through, that portion is tested elsewhere
        sot._translate_response = lambda arg: arg

        result = sot.rebuild(self.sess, name='nootoo',
                             admin_password='seekr3two',
                             image='http://image/2')

        self.assertIsInstance(result, server.Server)

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "name": "nootoo",
                "imageRef": "http://image/2",
                "adminPass": "seekr3two",
                "preserve_ephemeral": False
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.resize(self.sess, '2'))

        url = 'servers/IDENTIFIER/action'
        body = {"resize": {"flavorRef": "2"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_confirm_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.confirm_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"confirmResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_revert_resize(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.revert_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"revertResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_create_image(self):
        sot = server.Server(**EXAMPLE)
        name = 'noo'
        metadata = {'nu': 'image', 'created': 'today'}

        self.assertIsNone(sot.create_image(self.sess, name, metadata))

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name, 'metadata': metadata}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_create_image_minimal(self):
        sot = server.Server(**EXAMPLE)
        name = 'noo'

        self.assertIsNone(self.resp.body, sot.create_image(self.sess, name))

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=dict(sot.service), json=body, headers=headers)

    def test_add_security_group(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.add_security_group(self.sess, "group"))

        url = 'servers/IDENTIFIER/action'
        body = {"addSecurityGroup": {"name": "group"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_remove_security_group(self):
        sot = server.Server(**EXAMPLE)

        self.assertIsNone(sot.remove_security_group(self.sess, "group"))

        url = 'servers/IDENTIFIER/action'
        body = {"removeSecurityGroup": {"name": "group"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)
