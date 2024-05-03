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

from unittest import mock

from keystoneauth1 import adapter

from openstack.dns.v2 import zone
from openstack.tests.unit import base

IDENTIFIER = 'NAME'
EXAMPLE = {
    'attributes': {'tier': 'gold', 'ha': 'true'},
    'id': IDENTIFIER,
    'name': 'test.org',
    'email': 'joe@example.org',
    'type': 'PRIMARY',
    'ttl': 7200,
    'description': 'This is an example zone.',
    'status': 'ACTIVE',
    'shared': False,
}


class TestZone(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = None

    def test_basic(self):
        sot = zone.Zone()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('zones', sot.resources_key)
        self.assertEqual('/zones', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

        self.assertEqual('PATCH', sot.commit_method)

        self.assertDictEqual(
            {
                'description': 'description',
                'email': 'email',
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'status': 'status',
                'ttl': 'ttl',
                'type': 'type',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = zone.Zone(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE['email'], sot.email)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['ttl'], sot.ttl)
        self.assertEqual(EXAMPLE['type'], sot.type)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['shared'], sot.is_shared)

    def test_abandon(self):
        sot = zone.Zone(**EXAMPLE)
        self.assertIsNone(sot.abandon(self.sess))
        self.sess.post.assert_called_with(
            'zones/NAME/tasks/abandon', json=None
        )
