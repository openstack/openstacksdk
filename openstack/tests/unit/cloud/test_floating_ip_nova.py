# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_floating_ip_nova
----------------------------------

Tests Floating IP resource methods for nova-network
"""

from openstack.tests import fakes
from openstack.tests.unit import base


def get_fake_has_service(has_service):
    def fake_has_service(s):
        if s == 'network':
            return False
        return has_service(s)

    return fake_has_service


class TestFloatingIP(base.TestCase):
    mock_floating_ip_list_rep = [
        {
            'fixed_ip': None,
            'id': 1,
            'instance_id': None,
            'ip': '203.0.113.1',
            'pool': 'nova',
        },
        {
            'fixed_ip': None,
            'id': 2,
            'instance_id': None,
            'ip': '203.0.113.2',
            'pool': 'nova',
        },
        {
            'fixed_ip': '192.0.2.3',
            'id': 29,
            'instance_id': 'myself',
            'ip': '198.51.100.29',
            'pool': 'black_hole',
        },
    ]

    mock_floating_ip_pools = [
        {'id': 'pool1_id', 'name': 'nova'},
        {'id': 'pool2_id', 'name': 'pool2'},
    ]

    def assertAreInstances(self, elements, elem_type):
        for e in elements:
            self.assertIsInstance(e, elem_type)

    def setUp(self):
        super().setUp()

        self.fake_server = fakes.make_fake_server(
            'server-id',
            '',
            'ACTIVE',
            addresses={
                'test_pnztt_net': [
                    {
                        'OS-EXT-IPS:type': 'fixed',
                        'addr': '192.0.2.129',
                        'version': 4,
                        'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:ae:7d:42',
                    }
                ]
            },
        )

        self.cloud.has_service = get_fake_has_service(self.cloud.has_service)

    def test_list_floating_ips(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
            ]
        )
        floating_ips = self.cloud.list_floating_ips()

        self.assertIsInstance(floating_ips, list)
        self.assertEqual(3, len(floating_ips))
        self.assertAreInstances(floating_ips, dict)

        self.assert_calls()

    def test_list_floating_ips_with_filters(self):
        self.assertRaisesRegex(
            ValueError,
            "nova-network doesn't support server-side floating IPs filtering. "
            "Use the 'search_floating_ips' method instead",
            self.cloud.list_floating_ips,
            filters={'Foo': 42},
        )

    def test_search_floating_ips(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
            ]
        )

        floating_ips = self.cloud.search_floating_ips(
            filters={'attached': False}
        )

        self.assertIsInstance(floating_ips, list)
        self.assertEqual(2, len(floating_ips))
        self.assertAreInstances(floating_ips, dict)

        self.assert_calls()

    def test_get_floating_ip(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
            ]
        )

        floating_ip = self.cloud.get_floating_ip(id='29')

        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('198.51.100.29', floating_ip['floating_ip_address'])

        self.assert_calls()

    def test_get_floating_ip_not_found(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
            ]
        )

        floating_ip = self.cloud.get_floating_ip(id='666')

        self.assertIsNone(floating_ip)

        self.assert_calls()

    def test_get_floating_ip_by_id(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips', '1']
                    ),
                    json={'floating_ip': self.mock_floating_ip_list_rep[0]},
                ),
            ]
        )

        floating_ip = self.cloud.get_floating_ip_by_id(id='1')

        self.assertIsInstance(floating_ip, dict)
        self.assertEqual('203.0.113.1', floating_ip['floating_ip_address'])
        self.assert_calls()

    def test_create_floating_ip(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ip': self.mock_floating_ip_list_rep[1]},
                    validate=dict(json={'pool': 'nova'}),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips', '2']
                    ),
                    json={'floating_ip': self.mock_floating_ip_list_rep[1]},
                ),
            ]
        )

        self.cloud.create_floating_ip(network='nova')

        self.assert_calls()

    def test_available_floating_ip_existing(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep[:1]},
                ),
            ]
        )

        ip = self.cloud.available_floating_ip(network='nova')

        self.assertEqual(
            self.mock_floating_ip_list_rep[0]['ip'], ip['floating_ip_address']
        )
        self.assert_calls()

    def test_available_floating_ip_new(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': []},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ip': self.mock_floating_ip_list_rep[0]},
                    validate=dict(json={'pool': 'nova'}),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips', '1']
                    ),
                    json={'floating_ip': self.mock_floating_ip_list_rep[0]},
                ),
            ]
        )

        ip = self.cloud.available_floating_ip(network='nova')

        self.assertEqual(
            self.mock_floating_ip_list_rep[0]['ip'], ip['floating_ip_address']
        )
        self.assert_calls()

    def test_delete_floating_ip_existing(self):
        self.register_uris(
            [
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        append=['os-floating-ips', 'a-wild-id-appears'],
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': []},
                ),
            ]
        )

        ret = self.cloud.delete_floating_ip(floating_ip_id='a-wild-id-appears')

        self.assertTrue(ret)
        self.assert_calls()

    def test_delete_floating_ip_not_found(self):
        self.register_uris(
            [
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        append=['os-floating-ips', 'a-wild-id-appears'],
                    ),
                    status_code=404,
                ),
            ]
        )

        ret = self.cloud.delete_floating_ip(floating_ip_id='a-wild-id-appears')

        self.assertFalse(ret)
        self.assert_calls()

    def test_attach_ip_to_server(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        append=['servers', self.fake_server['id'], 'action'],
                    ),
                    validate=dict(
                        json={
                            "addFloatingIp": {
                                "address": "203.0.113.1",
                                "fixed_address": "192.0.2.129",
                            }
                        }
                    ),
                ),
            ]
        )

        self.cloud._attach_ip_to_server(
            server=self.fake_server,
            floating_ip=self.cloud._normalize_floating_ip(
                self.mock_floating_ip_list_rep[0]
            ),
            fixed_address='192.0.2.129',
        )

        self.assert_calls()

    def test_detach_ip_from_server(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        append=['servers', self.fake_server['id'], 'action'],
                    ),
                    validate=dict(
                        json={
                            "removeFloatingIp": {
                                "address": "203.0.113.1",
                            }
                        }
                    ),
                ),
            ]
        )

        self.cloud.detach_ip_from_server(
            server_id='server-id', floating_ip_id=1
        )
        self.assert_calls()

    def test_add_ip_from_pool(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', append=['os-floating-ips']
                    ),
                    json={'floating_ips': self.mock_floating_ip_list_rep},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute',
                        append=['servers', self.fake_server['id'], 'action'],
                    ),
                    validate=dict(
                        json={
                            "addFloatingIp": {
                                "address": "203.0.113.1",
                                "fixed_address": "192.0.2.129",
                            }
                        }
                    ),
                ),
            ]
        )

        server = self.cloud._add_ip_from_pool(
            server=self.fake_server,
            network='nova',
            fixed_address='192.0.2.129',
        )

        self.assertEqual(server, self.fake_server)
        self.assert_calls()

    def test_cleanup_floating_ips(self):
        # This should not call anything because it's unsafe on nova.
        self.assertFalse(self.cloud.delete_unattached_floating_ips())
