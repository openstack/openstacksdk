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

from openstack.identity.v3 import federation_protocol
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE: dict[str, Any] = {
    'id': IDENTIFIER,
    'idp_id': 'example_idp',
    'mapping_id': 'example_mapping',
}


class TestFederationProtocol(base.TestCase):
    def test_basic(self):
        sot = federation_protocol.FederationProtocol()
        self.assertEqual('protocol', sot.resource_key)
        self.assertEqual('protocols', sot.resources_key)
        self.assertEqual(
            '/OS-FEDERATION/identity_providers/%(idp_id)s/protocols',
            sot.base_path,
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_opts.method)
        self.assertEqual('PUT', sot.create_opts.method)

        self.assertDictEqual(
            {
                'id': 'id',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_encoded_paths(self):
        raw = 'name?#%2Fé'
        encoded = 'name%3F%23%252F%C3%A9'
        endpoint = self.get_mock_url('identity', base_url_append='v3')
        path = f'/OS-FEDERATION/identity_providers/{encoded}/protocols'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=endpoint + path,
                    json={'protocols': [{'id': raw}]},
                ),
                dict(
                    method='GET',
                    uri=endpoint + path + '/' + encoded,
                    json={'protocol': {'id': raw}},
                ),
            ]
        )
        protocols = list(
            federation_protocol.FederationProtocol.list(
                self.cloud.identity, idp_id=raw, paginated=False
            )
        )
        self.assertEqual(raw, protocols[0].idp_id)
        protocols[0].fetch(self.cloud.identity)
        self.assertEqual(raw, protocols[0].id)
        self.assertEqual(raw, protocols[0].idp_id)
        self.assert_calls()

    def test_make_it(self):
        sot = federation_protocol.FederationProtocol(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['idp_id'], sot.idp_id)
        self.assertEqual(EXAMPLE['mapping_id'], sot.mapping_id)
