#   Copyright 2021 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from openstack.network.v2 import local_ip_association
from openstack.tests.unit import base

EXAMPLE = {
    'local_ip_id': '0',
    'local_ip_address': '127.0.0.1',
    'fixed_port_id': '1',
    'fixed_ip': '127.0.0.2',
    'host': '2',
}


class TestLocalIP(base.TestCase):
    def test_basic(self):
        sot = local_ip_association.LocalIPAssociation()
        self.assertEqual('port_association', sot.resource_key)
        self.assertEqual('port_associations', sot.resources_key)
        self.assertEqual(
            '/local_ips/%(local_ip_id)s/port_associations', sot.base_path
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'fixed_port_id': 'fixed_port_id',
                'fixed_ip': 'fixed_ip',
                'host': 'host',
                'limit': 'limit',
                'marker': 'marker',
                'sort_dir': 'sort_dir',
                'sort_key': 'sort_key',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = local_ip_association.LocalIPAssociation(**EXAMPLE)
        self.assertEqual(EXAMPLE['local_ip_id'], sot.local_ip_id)
        self.assertEqual(EXAMPLE['local_ip_address'], sot.local_ip_address)
        self.assertEqual(EXAMPLE['fixed_port_id'], sot.fixed_port_id)
        self.assertEqual(EXAMPLE['fixed_ip'], sot.fixed_ip)
        self.assertEqual(EXAMPLE['host'], sot.host)
