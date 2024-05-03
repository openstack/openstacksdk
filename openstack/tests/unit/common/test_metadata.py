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

from openstack.common import metadata
from openstack import exceptions
from openstack import resource
from openstack.tests.unit import base
from openstack.tests.unit.test_resource import FakeResponse

IDENTIFIER = 'IDENTIFIER'


class TestMetadata(base.TestCase):
    def setUp(self):
        super().setUp()

        self.service_name = "service"
        self.base_path = "base_path"

        self.metadata_result = {"metadata": {"go": "cubs", "boo": "sox"}}
        self.meta_result = {"meta": {"oh": "yeah"}}

        class Test(resource.Resource, metadata.MetadataMixin):
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

        self.sot = Test.new(id="id")
        self.sot._prepare_request = mock.Mock(return_value=self.request)
        self.sot._translate_response = mock.Mock()

        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.get = mock.Mock(return_value=self.response)
        self.session.put = mock.Mock(return_value=self.response)
        self.session.post = mock.Mock(return_value=self.response)
        self.session.delete = mock.Mock(return_value=self.response)

    def test_metadata_attribute(self):
        res = self.sot
        self.assertTrue(hasattr(res, 'metadata'))

    def test_get_metadata(self):
        res = self.sot

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {'metadata': {'foo': 'bar'}}

        self.session.get.side_effect = [mock_response]

        result = res.fetch_metadata(self.session)
        # Check metadata attribute is updated
        self.assertDictEqual({'foo': 'bar'}, result.metadata)
        # Check passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata'
        self.session.get.assert_called_once_with(url)

    def test_set_metadata(self):
        res = self.sot

        result = res.set_metadata(self.session, {'foo': 'bar'})
        # Check metadata attribute is updated
        self.assertDictEqual({'foo': 'bar'}, res.metadata)
        # Check passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata'
        self.session.post.assert_called_once_with(
            url, json={'metadata': {'foo': 'bar'}}
        )

    def test_replace_metadata(self):
        res = self.sot

        result = res.replace_metadata(self.session, {'foo': 'bar'})
        # Check metadata attribute is updated
        self.assertDictEqual({'foo': 'bar'}, res.metadata)
        # Check passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata'
        self.session.put.assert_called_once_with(
            url, json={'metadata': {'foo': 'bar'}}
        )

    def test_delete_all_metadata(self):
        res = self.sot

        # Set some initial value to check removal
        res.metadata = {'foo': 'bar'}

        result = res.delete_metadata(self.session)
        # Check metadata attribute is updated
        self.assertEqual({}, res.metadata)
        # Check passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata'
        self.session.put.assert_called_once_with(url, json={'metadata': {}})

    def test_get_metadata_item(self):
        res = self.sot

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'meta': {'foo': 'bar'}}
        self.session.get.side_effect = [mock_response]

        result = res.get_metadata_item(self.session, 'foo')
        # Check tags attribute is updated
        self.assertEqual({'foo': 'bar'}, res.metadata)
        # Check the passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata/foo'
        self.session.get.assert_called_once_with(url)

    def test_delete_single_item(self):
        res = self.sot

        res.metadata = {'foo': 'bar', 'foo2': 'bar2'}

        result = res.delete_metadata_item(self.session, 'foo2')
        # Check metadata attribute is updated
        self.assertEqual({'foo': 'bar'}, res.metadata)
        # Check passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata/foo2'
        self.session.delete.assert_called_once_with(url)

    def test_delete_signle_item_empty(self):
        res = self.sot

        result = res.delete_metadata_item(self.session, 'foo2')
        # Check metadata attribute is updated
        self.assertEqual({}, res.metadata)
        # Check passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata/foo2'
        self.session.delete.assert_called_once_with(url)

    def test_get_metadata_item_not_exists(self):
        res = self.sot

        mock_response = mock.Mock()
        mock_response.status_code = 404
        mock_response.content = None
        self.session.get.side_effect = [mock_response]

        # ensure we get 404
        self.assertRaises(
            exceptions.NotFoundException,
            res.get_metadata_item,
            self.session,
            'dummy',
        )

    def test_set_metadata_item(self):
        res = self.sot

        # Set some initial value to check add
        res.metadata = {'foo': 'bar'}

        result = res.set_metadata_item(self.session, 'foo', 'black')
        # Check metadata attribute is updated
        self.assertEqual({'foo': 'black'}, res.metadata)
        # Check passed resource is returned
        self.assertEqual(res, result)
        url = self.base_path + '/' + res.id + '/metadata/foo'
        self.session.put.assert_called_once_with(
            url, json={'meta': {'foo': 'black'}}
        )
