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

import inspect
import mock
from openstack.tests.unit import base

from openstack.network.v2 import network
import openstack.network.v2 as network_resources
from openstack.network.v2.tag import TagMixin

ID = 'IDENTIFIER'


class TestTag(base.TestCase):

    @staticmethod
    def _create_network_resource(tags=None):
        tags = tags or []
        return network.Network(id=ID, name='test-net', tags=tags)

    def test_tags_attribute(self):
        net = self._create_network_resource()
        self.assertTrue(hasattr(net, 'tags'))
        self.assertIsInstance(net.tags, list)

    def test_set_tags(self):
        net = self._create_network_resource()
        sess = mock.Mock()
        result = net.set_tags(sess, ['blue', 'green'])
        # Check tags attribute is updated
        self.assertEqual(['blue', 'green'], net.tags)
        # Check the passed resource is returned
        self.assertEqual(net, result)
        url = 'networks/' + ID + '/tags'
        sess.put.assert_called_once_with(url,
                                         json={'tags': ['blue', 'green']})

    def test_tagged_resource_always_created_with_empty_tag_list(self):
        for _, module in inspect.getmembers(network_resources,
                                            inspect.ismodule):
            for _, resource in inspect.getmembers(module, inspect.isclass):
                if issubclass(resource, TagMixin) and resource != TagMixin:
                    x_resource = resource.new(
                        id="%s_ID" % resource.resource_key.upper())
                    self.assertIsNotNone(x_resource.tags)
                    self.assertEqual(x_resource.tags, list())
