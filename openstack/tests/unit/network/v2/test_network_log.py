# Copyright 2026 Openinfra Foundation
#
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

from typing import Any

from openstack.network.v2 import network_log
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE: dict[str, Any] = {
    'id': IDENTIFIER,
    'name': 'security group log',
    'description': 'Log for project demo.',
    'project_id': '92a5a4f4245a4abbafacb7ca73b027b0',
    'created_at': '2018-04-03T21:03:04Z',
    'updated_at': '2018-04-03T21:03:04Z',
    'revision_number': 1,
    'enabled': True,
    'event': 'ALL',
    'resource_type': 'security_group',
    'resource_id': '46ebaec0-0570-43ac-82f6-60d2b03168c4',
    'target_id': 'cf5dc5f6-0570-43ac-82f6-60d2b0316800',
}


class TestNetworkLog(base.TestCase):
    def test_basic(self):
        sot = network_log.Log()
        self.assertEqual('log', sot.resource_key)
        self.assertEqual('logs', sot.resources_key)
        self.assertEqual('/log/logs', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'id': 'id',
                'name': 'name',
                'project_id': 'project_id',
                'event': 'event',
                'resource_type': 'resource_type',
                'resource_id': 'resource_id',
                'target_id': 'target_id',
                'enabled': 'enabled',
                'revision_number': 'revision_number',
                'sort_dir': 'sort_dir',
                'sort_key': 'sort_key',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = network_log.Log(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertEqual(EXAMPLE['enabled'], sot.enabled)
        self.assertTrue(sot.enabled)
        self.assertEqual(EXAMPLE['event'], sot.event)
        self.assertEqual(EXAMPLE['resource_type'], sot.resource_type)
        self.assertEqual(EXAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(EXAMPLE['target_id'], sot.target_id)


class TestNetworkLoggableResource(base.TestCase):
    def test_basic(self):
        sot = network_log.LoggableResource()
        self.assertEqual('loggable_resource', sot.resource_key)
        self.assertEqual('loggable_resources', sot.resources_key)
        self.assertEqual('/log/loggable-resources', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                'type': 'type',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = network_log.LoggableResource(type='security_group')
        self.assertEqual('security_group', sot.type)
