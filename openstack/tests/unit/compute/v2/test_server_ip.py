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

from openstack.compute.v2 import server_ip

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'addr': '1',
    'network_label': '2',
    'server_id': '3',
    'version': '4',
}
BODY = {
    "addresses": {
        "public": [
            {
                "version": 4,
                "addr": "67.23.10.132"
            },
            {
                "version": 6,
                "addr": "::babe:67.23.10.132"
            },
            {
                "version": 4,
                "addr": "67.23.10.131"
            },
            {
                "version": 6,
                "addr": "::babe:4317:0A83"
            }
        ],
        "private": [
            {
                "version": 4,
                "addr": "10.176.42.16"
            },
            {
                "version": 6,
                "addr": "::babe:10.176.42.16"
            }
        ]
    }
}


class TestServerIP(testtools.TestCase):

    def test_basic(self):
        sot = server_ip.ServerIP()
        self.assertEqual('server_ip', sot.resource_key)
        self.assertEqual('server_ips', sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/ips', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = server_ip.ServerIP(EXAMPLE)
        self.assertEqual(EXAMPLE['addr'], sot.id)
        self.assertEqual(EXAMPLE['addr'], sot.addr)
        self.assertEqual(EXAMPLE['network_label'], sot.network_label)
        self.assertEqual(EXAMPLE['server_id'], sot.server_id)
        self.assertEqual(EXAMPLE['version'], sot.version)

    def test_list(self):
        sess = mock.Mock()
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=BODY)
        sess.get = mock.Mock(return_value=resp)
        path_args = {'server_id': IDENTIFIER}

        caps = server_ip.ServerIP.list(sess, path_args=path_args)

        caps = sorted(caps, key=lambda cap: cap.id)
        self.assertEqual(6, len(caps))
        self.assertEqual('10.176.42.16', caps[0].addr)
        self.assertEqual('private', caps[0].network_label)
        self.assertEqual(IDENTIFIER, caps[0].server_id)
        self.assertEqual(4, caps[0].version)
        self.assertEqual('67.23.10.131', caps[1].addr)
        self.assertEqual('public', caps[1].network_label)
        self.assertEqual(IDENTIFIER, caps[1].server_id)
        self.assertEqual(4, caps[1].version)
        self.assertEqual('67.23.10.132', caps[2].addr)
        self.assertEqual('public', caps[2].network_label)
        self.assertEqual(IDENTIFIER, caps[2].server_id)
        self.assertEqual(4, caps[2].version)
        self.assertEqual('::babe:10.176.42.16', caps[3].addr)
        self.assertEqual('private', caps[3].network_label)
        self.assertEqual(IDENTIFIER, caps[3].server_id)
        self.assertEqual(6, caps[3].version)
        self.assertEqual('::babe:4317:0A83', caps[4].addr)
        self.assertEqual('public', caps[4].network_label)
        self.assertEqual(IDENTIFIER, caps[4].server_id)
        self.assertEqual(6, caps[4].version)
        self.assertEqual('::babe:67.23.10.132', caps[5].addr)
        self.assertEqual('public', caps[5].network_label)
        self.assertEqual(IDENTIFIER, caps[5].server_id)
        self.assertEqual(6, caps[5].version)
