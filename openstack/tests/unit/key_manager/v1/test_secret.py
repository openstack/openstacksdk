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

from keystoneauth1 import adapter

from openstack import exceptions
from openstack.key_manager.v1 import secret
from openstack.tests.unit import base

ID_VAL = "123"
IDENTIFIER = f'http://localhost:9311/v1/secrets/{ID_VAL}'
STORE_ID = '11111111-1111-1111-1111-111111111111'
STORE_REF = f'http://localhost:9311/v1/secret-stores/{STORE_ID}'
EXAMPLE: dict[str, Any] = {
    'algorithm': '1',
    'bit_length': '2',
    'consumers': [
        {
            'service': 'image',
            'resource_type': 'image',
            'resource_id': '123e4567-e89b-12d3-a456-426614174000',
        },
    ],
    'content_types': {'default': '3'},
    'expiration': '2017-03-09T12:14:57.233772',
    'mode': '5',
    'name': '6',
    'secret_ref': IDENTIFIER,
    'secret_store_id': STORE_ID,
    'secret_store_ref': STORE_REF,
    'status': '8',
    'updated': '2015-03-09T12:15:57.233773',
    'created': '2015-03-09T12:15:57.233774',
    'secret_type': '9',
    'payload': '10',
    'payload_content_type': '11',
    'payload_content_encoding': '12',
}


class TestSecret(base.TestCase):
    def test_basic(self):
        sot = secret.Secret()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('secrets', sot.resources_key)
        self.assertEqual('/secrets', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('1.3', sot._max_microversion)

        self.assertDictEqual(
            {
                "name": "name",
                "mode": "mode",
                "bits": "bits",
                "secret_type": "secret_type",
                "acl_only": "acl_only",
                "created": "created",
                "updated": "updated",
                "expiration": "expiration",
                "sort": "sort",
                "algorithm": "alg",
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = secret.Secret(**EXAMPLE)
        self.assertEqual(EXAMPLE['algorithm'], sot.algorithm)
        self.assertEqual(EXAMPLE['bit_length'], sot.bit_length)
        self.assertEqual(EXAMPLE['consumers'], sot.consumers)
        self.assertEqual(EXAMPLE['content_types'], sot.content_types)
        self.assertEqual(EXAMPLE['expiration'], sot.expires_at)
        self.assertEqual(EXAMPLE['mode'], sot.mode)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['secret_ref'], sot.secret_ref)
        self.assertEqual(EXAMPLE['secret_ref'], sot.id)
        self.assertEqual(ID_VAL, sot.secret_id)
        self.assertEqual(EXAMPLE['secret_store_id'], sot.secret_store_id)
        self.assertEqual(EXAMPLE['secret_store_ref'], sot.secret_store_ref)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['secret_type'], sot.secret_type)
        self.assertEqual(EXAMPLE['payload'], sot.payload)
        self.assertEqual(
            EXAMPLE['payload_content_type'], sot.payload_content_type
        )
        self.assertEqual(
            EXAMPLE['payload_content_encoding'], sot.payload_content_encoding
        )

    def _session(
        self,
        default_microversion=None,
        microversion_range=(None, None),
    ):
        sess = mock.Mock(spec=adapter.Adapter)
        sess.default_microversion = default_microversion
        # Pre-seed the probe cache so tests don't issue a discovery GET.
        sess._key_manager_microversion_range = microversion_range
        return sess

    def test_fetch_metadata_only(self):
        metadata = {
            key: value
            for key, value in EXAMPLE.items()
            if not key.startswith('payload')
        }
        sess = self._session(microversion_range=('1.0', '1.3'))
        sess.get.return_value.status_code = 200
        sess.get.return_value.headers = {}
        sess.get.return_value.json.return_value = metadata
        sot = secret.Secret(id=ID_VAL)

        self.assertIs(sot, sot.fetch(sess))

        sess.get.assert_called_once_with(
            'secrets/123', microversion='1.3', params={}, skip_cache=False
        )
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['secret_store_id'], sot.secret_store_id)
        self.assertEqual(EXAMPLE['content_types'], sot.content_types)
        self.assertIsNone(sot.payload)

    def _test_payload(self, content_type, **attrs):
        sess = self._session(microversion_range=('1.0', '1.3'))
        sess.get.return_value.status_code = 200
        sess.get.return_value.content = b'secret info'
        sot = secret.Secret(secret_ref=IDENTIFIER, status='ACTIVE', **attrs)

        self.assertIs(sot, sot.fetch_payload(sess))

        sess.get.assert_called_once_with(
            'secrets/123/payload',
            headers={'Accept': content_type},
            microversion='1.3',
        )
        expected = (
            'secret info' if content_type == 'text/plain' else b'secret info'
        )
        self.assertEqual(expected, sot.payload)
        self.assertEqual('ACTIVE', sot.status)
        self.assertFalse(sot._body.dirty)

    def test_fetch_payload_explicit_content_type(self):
        self._test_payload(
            'some/type',
            payload_content_type='some/type',
            content_types={'default': 'other/type'},
        )

    def test_fetch_payload_default_content_type(self):
        self._test_payload(
            'application/octet-stream',
            content_types={'default': 'application/octet-stream'},
        )

    def test_fetch_payload_text(self):
        self._test_payload(
            'text/plain', content_types={'default': 'text/plain'}
        )

    def test_fetch_payload_no_content_type(self):
        sess = self._session()
        sot = secret.Secret(id=ID_VAL)

        self.assertIs(sot, sot.fetch_payload(sess))

        self.assertIsNone(sot.payload)
        sess.get.assert_not_called()

    def test_fetch_payload_missing_default_content_type(self):
        sess = self._session()
        sot = secret.Secret(id=ID_VAL, content_types={})

        self.assertIs(sot, sot.fetch_payload(sess))

        self.assertIsNone(sot.payload)
        sess.get.assert_not_called()

    def test_fetch_payload_not_found(self):
        sess = self._session()
        sess.get.return_value.status_code = 404
        sess.get.return_value.headers = {}
        sess.get.return_value.json.return_value = {}
        sess.get.return_value.content = b''
        sot = secret.Secret(
            id=ID_VAL, payload_content_type='application/octet-stream'
        )

        self.assertRaises(
            exceptions.NotFoundException, sot.fetch_payload, sess
        )

        sess.get.assert_called_once_with(
            'secrets/123/payload',
            headers={'Accept': 'application/octet-stream'},
            microversion=None,
        )
        self.assertIsNone(sot.payload)

    def test_fetch_payload_explicit_microversion(self):
        sot = secret.Secret(
            id=ID_VAL, payload_content_type='application/octet-stream'
        )
        sess = self._session()
        sess.get.return_value.status_code = 200
        sess.get.return_value.content = b'secret info'
        sot.fetch_payload(sess, microversion='1.1')
        sess.get.assert_called_once_with(
            'secrets/123/payload',
            headers={'Accept': 'application/octet-stream'},
            microversion='1.1',
        )

    def test_migrate_store(self):
        sot = secret.Secret(id=ID_VAL)
        sess = self._session(default_microversion='1.3')
        resp = mock.Mock()
        resp.status_code = 204
        sess.put.return_value = resp
        sot.migrate_store(sess, STORE_ID)
        sess.put.assert_called_once_with(
            f'secrets/123/secret-store/{STORE_ID}',
            microversion='1.3',
        )

    def test_migrate_store_explicit_microversion(self):
        sot = secret.Secret(id=ID_VAL)
        sess = self._session()
        resp = mock.Mock()
        resp.status_code = 204
        sess.put.return_value = resp
        sot.migrate_store(sess, STORE_ID, microversion='1.3')
        sess.put.assert_called_once_with(
            f'secrets/123/secret-store/{STORE_ID}',
            microversion='1.3',
        )
