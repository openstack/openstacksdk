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
    'version': '4',
}


class TestServerIP(testtools.TestCase):

    def test_basic(self):
        sot = server_ip.ServerIP()
        self.assertEqual('addresses', sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/ips', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = server_ip.ServerIP(**EXAMPLE)
        self.assertEqual(EXAMPLE['addr'], sot.address)
        self.assertEqual(EXAMPLE['network_label'], sot.network_label)
        self.assertEqual(EXAMPLE['version'], sot.version)

    def test_list(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp
        resp.json.return_value = {
            "addresses": {"label1": [{"version": 1, "addr": "a1"},
                                     {"version": 2, "addr": "a2"}],
                          "label2": [{"version": 3, "addr": "a3"},
                                     {"version": 4, "addr": "a4"}]}}

        ips = list(server_ip.ServerIP.list(sess, server_id=IDENTIFIER))

        self.assertEqual(4, len(ips))
        ips = sorted(ips, key=lambda ip: ip.version)

        self.assertEqual(type(ips[0]), server_ip.ServerIP)
        self.assertEqual(ips[0].network_label, "label1")
        self.assertEqual(ips[0].address, "a1")
        self.assertEqual(ips[0].version, 1)
        self.assertEqual(type(ips[1]), server_ip.ServerIP)
        self.assertEqual(ips[1].network_label, "label1")
        self.assertEqual(ips[1].address, "a2")
        self.assertEqual(ips[1].version, 2)
        self.assertEqual(type(ips[2]), server_ip.ServerIP)
        self.assertEqual(ips[2].network_label, "label2")
        self.assertEqual(ips[2].address, "a3")
        self.assertEqual(ips[2].version, 3)
        self.assertEqual(type(ips[3]), server_ip.ServerIP)
        self.assertEqual(ips[3].network_label, "label2")
        self.assertEqual(ips[3].address, "a4")
        self.assertEqual(ips[3].version, 4)

    def test_list_network_label(self):
        label = "label1"
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp
        resp.json.return_value = {label: [{"version": 1,
                                           "addr": "a1"},
                                          {"version": 2,
                                           "addr": "a2"}]}

        ips = list(server_ip.ServerIP.list(sess, server_id=IDENTIFIER,
                                           network_label=label))

        self.assertEqual(2, len(ips))
        ips = sorted(ips, key=lambda ip: ip.version)

        self.assertEqual(type(ips[0]), server_ip.ServerIP)
        self.assertEqual(ips[0].network_label, label)
        self.assertEqual(ips[0].address, "a1")
        self.assertEqual(ips[0].version, 1)
        self.assertEqual(type(ips[1]), server_ip.ServerIP)
        self.assertEqual(ips[1].network_label, label)
        self.assertEqual(ips[1].address, "a2")
        self.assertEqual(ips[1].version, 2)
