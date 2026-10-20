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

from openstack.key_manager.v1 import secret
from openstack.tests.unit import base

ID_VAL = "123"
IDENTIFIER = f'http://localhost:9311/v1/secrets/{ID_VAL}'
STORE_ID = '11111111-1111-1111-1111-111111111111'
STORE_REF = f'http://localhost:9311/v1/secret-stores/{STORE_ID}'
EXAMPLE: dict[str, Any] = {
    'algorithm': '1',
    'bit_length': '2',
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
        sess = mock.Mock()
        sess.default_microversion = default_microversion
        # Pre-seed the probe cache so tests don't issue a discovery GET.
        sess._key_manager_microversion_range = microversion_range
        return sess

    def test_get_no_payload(self):
        sot = secret.Secret(id="id")

        sess = self._session()
        rv = mock.Mock()
        return_body = {"status": "cool"}
        rv.json = mock.Mock(return_value=return_body)
        sess.get = mock.Mock(return_value=rv)

        sot.fetch(sess)

        sess.get.assert_called_once_with("secrets/id", microversion=None)

    def test_get_negotiates_microversion(self):
        sot = secret.Secret(id="id")

        sess = self._session(microversion_range=('1.0', '1.3'))
        rv = mock.Mock()
        return_body = {"status": "cool", "secret_store_id": STORE_ID}
        rv.json = mock.Mock(return_value=return_body)
        sess.get = mock.Mock(return_value=rv)

        sot.fetch(sess)

        sess.get.assert_called_once_with("secrets/id", microversion='1.3')
        self.assertEqual(STORE_ID, sot.secret_store_id)

    def _test_payload(self, sot, metadata, content_type="some/type"):
        metadata_response = mock.Mock()
        # Use copy because the dict gets consumed.
        metadata_response.json = mock.Mock(return_value=metadata.copy())

        payload_response = mock.Mock()
        payload = b"secret info"
        payload_response.content = payload

        sess = self._session()
        sess.get = mock.Mock(side_effect=[metadata_response, payload_response])

        rv = sot.fetch(sess)

        sess.get.assert_has_calls(
            [
                mock.call(
                    "secrets/id",
                    microversion=None,
                ),
                mock.call(
                    "secrets/id/payload",
                    headers={"Accept": content_type},
                    skip_cache=False,
                    microversion=None,
                ),
            ]
        )

        expected_payload: str | bytes
        if content_type == "text/plain":
            expected_payload = payload.decode("utf-8")
        else:
            expected_payload = payload
        self.assertEqual(rv.payload, expected_payload)
        self.assertEqual(rv.status, metadata["status"])

    def test_get_with_payload_from_argument(self):
        metadata = {"status": "great"}
        content_type = "some/type"
        sot = secret.Secret(id="id", payload_content_type=content_type)
        self._test_payload(sot, metadata, content_type)

    def test_get_with_payload_from_content_types(self):
        content_type = "some/type"
        metadata = {
            "status": "fine",
            "content_types": {"default": content_type},
        }
        sot = secret.Secret(id="id")
        self._test_payload(sot, metadata, content_type)

    def test_get_with_text_payload(self):
        content_type = "text/plain"
        metadata = {
            "status": "fine",
            "content_types": {"default": content_type},
        }
        sot = secret.Secret(id="id")
        self._test_payload(sot, metadata, content_type)

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
