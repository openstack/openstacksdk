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

import datetime

import testtools

from openstack.network.v2 import subnet_pool

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'min_prefixlen': 8,
    'default_prefixlen': 24,
    'id': IDENTIFIER,
    'max_prefixlen': 32,
    'name': 'private-subnet_pool',
    'default_quota': 24,
    'tenant_id': '10',
    'prefixes': ['10.0.2.0/24', '10.0.4.0/24'],
    'ip_version': 4,
    'shared': True,
    'address_scope_id': '11',
    'description': '12',
    'created_at': '2016-03-09T12:14:57.233772',
    'updated_at': '2016-07-09T12:14:57.233772',
    'is_default': True,
}


class TestSubnetpool(testtools.TestCase):

    def test_basic(self):
        sot = subnet_pool.SubnetPool()
        self.assertEqual('subnetpool', sot.resource_key)
        self.assertEqual('subnetpools', sot.resources_key)
        self.assertEqual('/subnetpools', sot.base_path)
        self.assertEqual('network', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = subnet_pool.SubnetPool(EXAMPLE)
        self.assertEqual(EXAMPLE['min_prefixlen'],
                         sot.minimum_prefix_length)
        self.assertEqual(EXAMPLE['default_prefixlen'],
                         sot.default_prefix_length)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['max_prefixlen'],
                         sot.maximum_prefix_length)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['default_quota'], sot.default_quota)
        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(EXAMPLE['prefixes'], sot.prefixes)
        self.assertEqual(EXAMPLE['ip_version'], sot.ip_version)
        self.assertTrue(sot.is_shared)
        self.assertEqual(EXAMPLE['address_scope_id'], sot.address_scope_id)
        self.assertEqual(EXAMPLE['description'], sot.description)
        dt = datetime.datetime(2016, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        dt = datetime.datetime(2016, 7, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))
        self.assertTrue(sot.is_default)
