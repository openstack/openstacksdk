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

from openstack.network.v2 import local_ip
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'created_at': '0',
    'id': IDENTIFIER,
    'name': '1',
    'description': '2',
    'project_id': '3',
    'local_port_id': '4',
    'network_id': '5',
    'local_ip_address': '127.0.0.1',
    'ip_mode': 'translate',
    'revision_number': '6',
    'updated_at': '7',
}


class TestLocalIP(base.TestCase):
    def test_basic(self):
        sot = local_ip.LocalIP()
        self.assertEqual('local_ip', sot.resource_key)
        self.assertEqual('local_ips', sot.resources_key)
        self.assertEqual('/local_ips', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                "name": "name",
                "description": "description",
                "project_id": "project_id",
                "network_id": "network_id",
                "local_port_id": "local_port_id",
                "local_ip_address": "local_ip_address",
                "ip_mode": "ip_mode",
                "sort_key": "sort_key",
                "sort_dir": "sort_dir",
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = local_ip.LocalIP(**EXAMPLE)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['local_port_id'], sot.local_port_id)
        self.assertEqual(EXAMPLE['network_id'], sot.network_id)
        self.assertEqual(EXAMPLE['local_ip_address'], sot.local_ip_address)
        self.assertEqual(EXAMPLE['ip_mode'], sot.ip_mode)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
