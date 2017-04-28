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

from openstack.network.v2 import network


ID = 'IDENTIFIER'


class TestTag(testtools.TestCase):

    @staticmethod
    def _create_resource(tags=None):
        tags = tags or []
        return network.Network(id=ID, name='test-net', tags=tags)

    def test_tags_attribute(self):
        net = self._create_resource()
        self.assertTrue(hasattr(net, 'tags'))
        self.assertIsInstance(net.tags, list)

    def test_set_tags(self):
        net = self._create_resource()
        sess = mock.Mock()
        result = net.set_tags(sess, ['blue', 'green'])
        # Check tags attribute is updated
        self.assertEqual(['blue', 'green'], net.tags)
        # Check the passed resource is returned
        self.assertEqual(net, result)
        url = 'networks/' + ID + '/tags'
        sess.put.assert_called_once_with(url, endpoint_filter=net.service,
                                         json={'tags': ['blue', 'green']})
