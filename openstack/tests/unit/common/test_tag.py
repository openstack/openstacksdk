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

from openstack.common import tag
from openstack import exceptions
from openstack import resource
from openstack.tests.unit import base
from openstack.tests.unit.test_resource import FakeResponse


class TestTagMixin(base.TestCase):
    def setUp(self):
        super().setUp()

        self.service_name = "service"
        self.base_path = "base_path"

        class Test(resource.Resource, tag.TagMixin):
            service = self.service_name
            base_path = self.base_path
            resources_key = 'resources'
            allow_create = True
            allow_fetch = True
            allow_head = True
            allow_commit = True
            allow_delete = True
            allow_list = True

        self.test_class = Test

        self.request = mock.Mock(spec=resource._Request)
        self.request.url = "uri"
        self.request.body = "body"
        self.request.headers = "headers"

        self.response = FakeResponse({})

        self.sot = Test.new(id="id", tags=[])
        self.sot._prepare_request = mock.Mock(return_value=self.request)
        self.sot._translate_response = mock.Mock()

        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.get = mock.Mock(return_value=self.response)
        self.session.put = mock.Mock(return_value=self.response)
        self.session.delete = mock.Mock(return_value=self.response)

    def test_tags_attribute(self):
        res = self.sot
        self.assertTrue(hasattr(res, 'tags'))
        self.assertIsInstance(res.tags, list)

    def test_fetch_tags(self):
        res = self.sot
        sess = self.session

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {'tags': ['blue1', 'green1']}

        sess.get.side_effect = [mock_response]

        result = res.fetch_tags(sess)
        # Check tags attribute is updated
        self.assertEqual(['blue1', 'green1'], res.tags)
        # Check the passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/tags'
        sess.get.assert_called_once_with(url)

    def test_set_tags(self):
        res = self.sot
        sess = self.session

        # Set some initial value to check rewrite
        res.tags = ['blue_old', 'green_old']

        result = res.set_tags(sess, ['blue', 'green'])
        # Check tags attribute is updated
        self.assertEqual(['blue', 'green'], res.tags)
        # Check the passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/tags'
        sess.put.assert_called_once_with(url, json={'tags': ['blue', 'green']})

    def test_remove_all_tags(self):
        res = self.sot
        sess = self.session

        # Set some initial value to check removal
        res.tags = ['blue_old', 'green_old']

        result = res.remove_all_tags(sess)
        # Check tags attribute is updated
        self.assertEqual([], res.tags)
        # Check the passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/tags'
        sess.delete.assert_called_once_with(url)

    def test_remove_single_tag(self):
        res = self.sot
        sess = self.session

        res.tags = ['blue', 'dummy']

        result = res.remove_tag(sess, 'dummy')
        # Check tags attribute is updated
        self.assertEqual(['blue'], res.tags)
        # Check the passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/tags/dummy'
        sess.delete.assert_called_once_with(url)

    def test_check_tag_exists(self):
        res = self.sot
        sess = self.session

        sess.get.side_effect = [FakeResponse(None, 202)]

        result = res.check_tag(sess, 'blue')
        # Check tags attribute is updated
        self.assertEqual([], res.tags)
        # Check the passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/tags/blue'
        sess.get.assert_called_once_with(url)

    def test_check_tag_not_exists(self):
        res = self.sot
        sess = self.session

        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.links = {}
        mock_response.content = None

        sess.get.side_effect = [mock_response]

        # ensure we get 404
        self.assertRaises(
            exceptions.NotFoundException,
            res.check_tag,
            sess,
            'dummy',
        )

    def test_add_tag(self):
        res = self.sot
        sess = self.session

        # Set some initial value to check add
        res.tags = ['blue', 'green']

        result = res.add_tag(sess, 'lila')
        # Check tags attribute is updated
        self.assertEqual(['blue', 'green', 'lila'], res.tags)
        # Check the passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/tags/lila'
        sess.put.assert_called_once_with(url)

    def test_tagged_resource_always_created_with_empty_tag_list(self):
        res = self.sot

        self.assertIsNotNone(res.tags)
        self.assertEqual(res.tags, list())
