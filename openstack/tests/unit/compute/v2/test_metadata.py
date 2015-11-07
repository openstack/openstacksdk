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

import mock
import testtools

from openstack.compute.v2 import server

IDENTIFIER = 'IDENTIFIER'

# NOTE: The implementation for metadata is done via a mixin class that both
# the server and image resources inherit from. Currently this test class
# uses the Server resource to test it. Ideally it would be parameterized
# to run with both Server and Image when the tooling for subtests starts
# working.


class TestMetadata(testtools.TestCase):

    def setUp(self):
        super(TestMetadata, self).setUp()
        self.metadata_result = {"metadata": {"go": "cubs", "boo": "sox"}}
        self.meta_result = {"meta": {"oh": "yeah"}}

    def test_get_all_metadata_Server(self):
        self._test_get_all_metadata(server.Server({"id": IDENTIFIER}))

    def test_get_all_metadata_ServerDetail(self):
        # This is tested explicitly so we know ServerDetail items are
        # properly having /detail stripped out of their base_path.
        self._test_get_all_metadata(server.ServerDetail({"id": IDENTIFIER}))

    def _test_get_all_metadata(self, sot):
        response = mock.Mock()
        response.json.return_value = self.metadata_result
        sess = mock.Mock()
        sess.get.return_value = response

        result = sot.get_metadata(sess)

        self.assertEqual(result, self.metadata_result["metadata"])
        sess.get.assert_called_once_with("servers/IDENTIFIER/metadata",
                                         headers={},
                                         endpoint_filter=sot.service)

    def test_get_one_metadata(self):
        response = mock.Mock()
        response.json.return_value = self.meta_result
        sess = mock.Mock()
        sess.get.return_value = response

        sot = server.Server({"id": IDENTIFIER})

        key = "lol"
        result = sot.get_metadata(sess, key)

        self.assertEqual(result, self.meta_result["meta"])
        sess.get.assert_called_once_with("servers/IDENTIFIER/metadata/" + key,
                                         headers={},
                                         endpoint_filter=sot.service)

    def test_create_metadata_bad_type(self):
        sess = mock.Mock()
        sess.put = mock.Mock()

        sot = server.Server({"id": IDENTIFIER})
        self.assertRaises(ValueError,
                          sot.create_metadata, sess, some_key=True)

    def test_create_metadata(self):
        metadata = {"first": "1", "second": "2"}
        responses = []
        for key, value in metadata.items():
            response = mock.Mock()
            response.json.return_value = {"meta": {key: value}}
            responses.append(response)

        sess = mock.Mock()
        sess.put.side_effect = responses

        sot = server.Server({"id": IDENTIFIER})

        result = sot.create_metadata(sess, **metadata)

        self.assertEqual(result, dict([(k, v) for k, v in metadata.items()]))

        # assert_called_with depends on sequence, which doesn't work nicely
        # with all of the dictionaries we're working with here. Build up
        # our own list of calls and check that they've happend
        calls = []
        for key in metadata.keys():
            calls.append(mock.call("servers/IDENTIFIER/metadata/" + key,
                                   endpoint_filter=sot.service,
                                   headers={},
                                   json={"meta": {key: metadata[key]}}))

        sess.put.assert_has_calls(calls, any_order=True)

    def test_replace_metadata(self):
        response = mock.Mock()
        response.json.return_value = self.metadata_result
        sess = mock.Mock()
        sess.put.return_value = response

        sot = server.Server({"id": IDENTIFIER})

        new_meta = {"lol": "rofl"}

        result = sot.replace_metadata(sess, **new_meta)

        self.assertEqual(result, self.metadata_result["metadata"])
        sess.put.assert_called_once_with("servers/IDENTIFIER/metadata",
                                         endpoint_filter=sot.service,
                                         headers={},
                                         json={"metadata": new_meta})

    def test_replace_metadata_clear(self):
        empty = {}

        response = mock.Mock()
        response.json.return_value = {"metadata": empty}
        sess = mock.Mock()
        sess.put.return_value = response

        sot = server.Server({"id": IDENTIFIER})

        result = sot.replace_metadata(sess)

        self.assertEqual(result, empty)
        sess.put.assert_called_once_with("servers/IDENTIFIER/metadata",
                                         endpoint_filter=sot.service,
                                         headers={},
                                         json={"metadata": empty})

    def test_update_metadata(self):
        response = mock.Mock()
        response.json.return_value = self.metadata_result
        sess = mock.Mock()
        sess.post.return_value = response

        sot = server.Server({"id": IDENTIFIER})

        updated_meta = {"lol": "rofl"}

        result = sot.update_metadata(sess, **updated_meta)

        self.assertEqual(result, self.metadata_result["metadata"])
        sess.post.assert_called_once_with("servers/IDENTIFIER/metadata",
                                          endpoint_filter=sot.service,
                                          headers={},
                                          json={"metadata": updated_meta})

    def test_delete_metadata(self):
        sess = mock.Mock()
        sess.delete.return_value = None

        sot = server.Server({"id": IDENTIFIER})

        key = "hey"

        result = sot.delete_metadata(sess, key)

        self.assertIsNone(result)
        sess.delete.assert_called_once_with(
            "servers/IDENTIFIER/metadata/" + key,
            headers={"Accept": ""},
            endpoint_filter=sot.service)
