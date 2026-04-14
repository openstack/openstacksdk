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
from unittest import mock

from keystoneauth1 import adapter

from openstack.identity.v3 import registered_limit
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "service_id": "8ac43bb0926245cead88676a96c750d3",
    "region_id": 'RegionOne',
    "resource_name": 'cores',
    "default_limit": 10,
    "description": "compute cores",
    "links": {"self": "http://example.com/v3/registered_limit_1"},
}


class TestRegistered_limit(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.status_code = 200
        self.resp.headers = {}
        self.resp.json = mock.Mock(return_value={})
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = None
        self.sess.retriable_status_codes = None
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_basic(self):
        sot = registered_limit.RegisteredLimit()
        self.assertEqual('registered_limit', sot.resource_key)
        self.assertEqual('registered_limits', sot.resources_key)
        self.assertEqual('/registered_limits', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

        self.assertDictEqual(
            {
                'service_id': 'service_id',
                'region_id': 'region_id',
                'resource_name': 'resource_name',
                'marker': 'marker',
                'limit': 'limit',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = registered_limit.RegisteredLimit(**EXAMPLE)
        self.assertEqual(EXAMPLE['service_id'], sot.service_id)
        self.assertEqual(EXAMPLE['region_id'], sot.region_id)
        self.assertEqual(EXAMPLE['resource_name'], sot.resource_name)
        self.assertEqual(EXAMPLE['default_limit'], sot.default_limit)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['links'], sot.links)

    def test_create(self):
        sot = registered_limit.RegisteredLimit(**EXAMPLE)
        sot._translate_response = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)

        sot.create(self.sess)

        self.sess.post.assert_called_with(
            '/registered_limits',
            json={'registered_limits': [copy.deepcopy(EXAMPLE)]},
            microversion=None,
            headers={},
            params={},
        )

    def test_commit(self):
        sot = registered_limit.RegisteredLimit(id=IDENTIFIER, default_limit=20)
        self.sess.patch = mock.Mock(return_value=self.resp)

        sot.commit(self.sess)

        self.sess.patch.assert_called_with(
            f'registered_limits/{IDENTIFIER}',
            json={'registered_limit': {'default_limit': 20}},
            headers={},
            microversion=None,
        )
