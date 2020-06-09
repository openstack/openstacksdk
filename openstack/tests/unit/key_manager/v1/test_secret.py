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

from openstack.key_manager.v1 import secret
from openstack.tests.unit import base

ID_VAL = "123"
IDENTIFIER = 'http://localhost:9311/v1/secrets/%s' % ID_VAL
EXAMPLE = {
    'algorithm': '1',
    'bit_length': '2',
    'content_types': {'default': '3'},
    'expiration': '2017-03-09T12:14:57.233772',
    'mode': '5',
    'name': '6',
    'secret_ref': IDENTIFIER,
    'status': '8',
    'updated': '2015-03-09T12:15:57.233773',
    'created': '2015-03-09T12:15:57.233774',
    'secret_type': '9',
    'payload': '10',
    'payload_content_type': '11',
    'payload_content_encoding': '12'
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

        self.assertDictEqual({"name": "name",
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
                              "marker": "marker"},
                             sot._query_mapping._mapping)

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
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated_at)
        self.assertEqual(EXAMPLE['secret_type'], sot.secret_type)
        self.assertEqual(EXAMPLE['payload'], sot.payload)
        self.assertEqual(EXAMPLE['payload_content_type'],
                         sot.payload_content_type)
        self.assertEqual(EXAMPLE['payload_content_encoding'],
                         sot.payload_content_encoding)

    def test_get_no_payload(self):
        sot = secret.Secret(id="id")

        sess = mock.Mock()
        rv = mock.Mock()
        return_body = {"status": "cool"}
        rv.json = mock.Mock(return_value=return_body)
        sess.get = mock.Mock(return_value=rv)

        sot.fetch(sess)

        sess.get.assert_called_once_with("secrets/id")

    def _test_payload(self, sot, metadata, content_type):
        content_type = "some/type"

        metadata_response = mock.Mock()
        # Use copy because the dict gets consumed.
        metadata_response.json = mock.Mock(return_value=metadata.copy())

        payload_response = mock.Mock()
        payload = "secret info"
        payload_response.text = payload

        sess = mock.Mock()
        sess.get = mock.Mock(side_effect=[metadata_response, payload_response])

        rv = sot.fetch(sess)

        sess.get.assert_has_calls(
            [mock.call("secrets/id",),
             mock.call("secrets/id/payload",
                       headers={"Accept": content_type})])

        self.assertEqual(rv.payload, payload)
        self.assertEqual(rv.status, metadata["status"])

    def test_get_with_payload_from_argument(self):
        metadata = {"status": "great"}
        content_type = "some/type"
        sot = secret.Secret(id="id", payload_content_type=content_type)
        self._test_payload(sot, metadata, content_type)

    def test_get_with_payload_from_content_types(self):
        content_type = "some/type"
        metadata = {"status": "fine",
                    "content_types": {"default": content_type}}
        sot = secret.Secret(id="id")
        self._test_payload(sot, metadata, content_type)
