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
import datetime

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
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = server.Server(EXAMPLE)
        self.assertEqual(EXAMPLE['accessIPv4'], sot.access_ipv4)
        self.assertEqual(EXAMPLE['accessIPv6'], sot.access_ipv6)
        self.assertEqual(EXAMPLE['addresses'], sot.addresses)
        dt = datetime.datetime(2015, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
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
        dt = datetime.datetime(2015, 3, 9, 12, 15, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)

    def test_detail(self):
        sot = server.ServerDetail()
        self.assertEqual('server', sot.resource_key)
        self.assertEqual('servers', sot.resources_key)
        self.assertEqual('/servers/detail', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_create_body(self):
        params = copy.deepcopy(EXAMPLE)
        params['scheduler_hints'] = {'group': 'GROUP1_ID'}
        body = server.Server._get_create_body(params)
        self.assertNotIn('scheduler_hints', body)
        self.assertEqual({'group': 'GROUP1_ID'}, body['os:scheduler_hints'])

    def test_change_passowrd(self):
        sot = server.Server(EXAMPLE)

        self.assertEqual(self.resp.body, sot.change_password(self.sess, 'a'))

        url = 'servers/IDENTIFIER/action'
        body = {"changePassword": {"adminPass": "a"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_reboot(self):
        sot = server.Server(EXAMPLE)

        self.assertEqual(self.resp.body, sot.reboot(self.sess, 'HARD'))

        url = 'servers/IDENTIFIER/action'
        body = {"reboot": {"type": "HARD"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_rebuild(self):
        sot = server.Server(EXAMPLE)

        self.assertEqual(
            self.resp.body,
            sot.rebuild(
                self.sess,
                name='noo',
                image_href='http://image/1',
                admin_password='seekr3t',
                access_ipv4="12.34.56.78",
                access_ipv6="fe80::100",
                metadata={"meta var": "meta val"},
                personality=[{"path": "/etc/motd", "contents": "foo"}],
            )
        )

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
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_rebuild_minimal(self):
        sot = server.Server(EXAMPLE)

        self.assertEqual(
            self.resp.body,
            sot.rebuild(
                self.sess,
                name='nootoo',
                image_href='http://image/2',
                admin_password='seekr3two',
            )
        )

        url = 'servers/IDENTIFIER/action'
        body = {
            "rebuild": {
                "name": "nootoo",
                "imageRef": "http://image/2",
                "adminPass": "seekr3two",
            }
        }
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_resize(self):
        sot = server.Server(EXAMPLE)

        self.assertEqual(self.resp.body, sot.resize(self.sess, '2'))

        url = 'servers/IDENTIFIER/action'
        body = {"resize": {"flavorRef": "2"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_confirm_resize(self):
        sot = server.Server(EXAMPLE)

        self.assertEqual(self.resp.body, sot.confirm_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"confirmResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_revert_resize(self):
        sot = server.Server(EXAMPLE)

        self.assertEqual(self.resp.body, sot.revert_resize(self.sess))

        url = 'servers/IDENTIFIER/action'
        body = {"revertResize": None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_create_image(self):
        sot = server.Server(EXAMPLE)
        name = 'noo'
        metadata = {'nu': 'image', 'created': 'today'}

        self.assertEqual(
            self.resp.body,
            sot.create_image(self.sess, name, metadata)
        )

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name, 'metadata': metadata}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=sot.service, json=body, headers=headers)

    def test_create_image_minimal(self):
        sot = server.Server(EXAMPLE)
        name = 'noo'

        self.assertEqual(
            self.resp.body,
            sot.create_image(self.sess, name)
        )

        url = 'servers/IDENTIFIER/action'
        body = {"createImage": {'name': name}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, endpoint_filter=dict(sot.service), json=body, headers=headers)

    def test_get_ips(self):
        name = "jenkins"
        fixed = {
            "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:f9:58:b4",
            "version": 4,
            "addr": "10.3.3.8",
            "OS-EXT-IPS:type": "fixed",
        }
        float1 = {
            "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:f9:58:b4",
            "version": 4,
            "addr": "15.125.3.1",
            "OS-EXT-IPS:type": "floating",
        }
        float2 = {
            "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:f9:58:b4",
            "version": 4,
            "addr": "15.125.3.2",
            "OS-EXT-IPS:type": "floating",
        }

        addresses = {name: [fixed]}
        attrs = {'id': IDENTIFIER, 'name': name, 'addresses': addresses}
        sot = server.Server(attrs=attrs)
        self.assertEqual([], sot.get_floating_ips())

        addresses = {name: [fixed, float1, float2]}
        attrs = {'id': IDENTIFIER, 'name': name, 'addresses': addresses}
        sot = server.Server(attrs=attrs)
        self.assertEqual(["15.125.3.1", "15.125.3.2"], sot.get_floating_ips())

        addresses = {name: [float1, fixed]}
        attrs = {'id': IDENTIFIER, 'name': name, 'addresses': addresses}
        sot = server.Server(attrs=attrs)
        self.assertEqual(["15.125.3.1"], sot.get_floating_ips())
