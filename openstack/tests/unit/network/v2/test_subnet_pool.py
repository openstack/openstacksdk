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
from unittest import mock

from openstack import exceptions
from openstack.network.v2 import subnet_pool
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE: dict[str, Any] = {
    'address_scope_id': '1',
    'created_at': '2',
    'default_prefixlen': 3,
    'default_quota': 4,
    'description': '5',
    'id': IDENTIFIER,
    'ip_version': 6,
    'is_default': True,
    'max_prefixlen': 7,
    'min_prefixlen': 8,
    'name': '9',
    'prefixes': ['10', '11'],
    'revision_number': 12,
    'shared': True,
    'project_id': '13',
    'updated_at': '14',
}


class TestSubnetpool(base.TestCase):
    def test_basic(self):
        sot = subnet_pool.SubnetPool()
        self.assertEqual('subnetpool', sot.resource_key)
        self.assertEqual('subnetpools', sot.resources_key)
        self.assertEqual('/subnetpools', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = subnet_pool.SubnetPool(**EXAMPLE)
        self.assertEqual(EXAMPLE['address_scope_id'], sot.address_scope_id)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(
            EXAMPLE['default_prefixlen'], sot.default_prefix_length
        )
        self.assertEqual(EXAMPLE['default_quota'], sot.default_quota)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['ip_version'], sot.ip_version)
        self.assertTrue(sot.is_default)
        self.assertEqual(EXAMPLE['max_prefixlen'], sot.maximum_prefix_length)
        self.assertEqual(EXAMPLE['min_prefixlen'], sot.minimum_prefix_length)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['prefixes'], sot.prefixes)
        self.assertEqual(EXAMPLE['revision_number'], sot.revision_number)
        self.assertTrue(sot.is_shared)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)

    def test_subnet_onboard(self):
        sot = subnet_pool.SubnetPool(**EXAMPLE)
        response = mock.Mock()
        response.body = {"subnetpool_id": "3", "cid": "1.2.3.4"}
        response.json = mock.Mock(return_value=response.body)
        response.status_code = 200
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        body = {"network_id": "3"}
        self.assertEqual(response.body, sot.subnet_onboard(sess, **body))

        url = 'subnetpools/IDENTIFIER/onboard_network_subnets'
        sess.put.assert_called_with(url, json=body)

    def test_subnet_onboard_4xx(self):
        sot = subnet_pool.SubnetPool(**EXAMPLE)
        response = mock.Mock()
        msg = '.*borked'
        response.body = {'NeutronError': {'message': msg}}
        response.json = mock.Mock(return_value=response.body)
        response.ok = False
        response.status_code = 409
        response.headers = {'content-type': 'application/json'}
        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        body = {"network_id": "3"}
        with self.assertRaises(exceptions.ConflictException, msg=msg):
            sot.subnet_onboard(sess, **body)
