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

    def test_set_metadata(self):
        response = mock.Mock()
        response.json.return_value = self.metadata_result
        sess = mock.Mock()
        sess.post.return_value = response

        sot = server.Server({"id": IDENTIFIER})

        set_meta = {"lol": "rofl"}

        result = sot.set_metadata(sess, **set_meta)

        self.assertEqual(result, self.metadata_result["metadata"])
        sess.post.assert_called_once_with("servers/IDENTIFIER/metadata",
                                          endpoint_filter=sot.service,
                                          headers={},
                                          json={"metadata": set_meta})

    def test_delete_metadata(self):
        sess = mock.Mock()
        sess.delete.return_value = None

        sot = server.Server({"id": IDENTIFIER})

        key = "hey"

        sot.delete_metadata(sess, [key])

        sess.delete.assert_called_once_with(
            "servers/IDENTIFIER/metadata/" + key,
            headers={"Accept": ""},
            endpoint_filter=sot.service)
