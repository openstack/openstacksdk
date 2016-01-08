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

from openstack import exceptions
from openstack import proxy
from openstack import resource


class DeleteableResource(resource.Resource):
    allow_delete = True


class UpdateableResource(resource.Resource):
    allow_update = True


class CreateableResource(resource.Resource):
    allow_create = True


class RetrieveableResource(resource.Resource):
    allow_retrieve = True


class ListableResource(resource.Resource):
    allow_list = True


class HeadableResource(resource.Resource):
    allow_head = True


class Test_check_resource(testtools.TestCase):

    def setUp(self):
        super(Test_check_resource, self).setUp()

        def method(self, expected_type, value):
            return value

        self.sot = mock.Mock()
        self.sot.method = method

    def _test_correct(self, value):
        decorated = proxy._check_resource(strict=False)(self.sot.method)
        rv = decorated(self.sot, resource.Resource, value)

        self.assertEqual(value, rv)

    def test_correct_resource(self):
        res = resource.Resource()
        self._test_correct(res)

    def test_notstrict_id(self):
        self._test_correct("abc123-id")

    def test_strict_id(self):
        decorated = proxy._check_resource(strict=True)(self.sot.method)
        self.assertRaisesRegexp(ValueError, "A Resource must be passed",
                                decorated, self.sot, resource.Resource,
                                "this-is-not-a-resource")

    def test_incorrect_resource(self):
        class OneType(resource.Resource):
            pass

        class AnotherType(resource.Resource):
            pass

        value = AnotherType()
        decorated = proxy._check_resource(strict=False)(self.sot.method)
        self.assertRaisesRegexp(ValueError,
                                "Expected OneType but received AnotherType",
                                decorated, self.sot, OneType, value)


class TestProxyDelete(testtools.TestCase):

    def setUp(self):
        super(TestProxyDelete, self).setUp()

        self.session = mock.Mock()

        self.fake_id = 1
        self.res = mock.Mock(spec=DeleteableResource)
        self.res.id = self.fake_id
        self.res.delete = mock.Mock()

        self.sot = proxy.BaseProxy(self.session)
        DeleteableResource.existing = mock.Mock(return_value=self.res)

    def test_delete(self):
        self.sot._delete(DeleteableResource, self.res)
        self.res.delete.assert_called_with(self.session)

        self.sot._delete(DeleteableResource, self.fake_id)
        DeleteableResource.existing.assert_called_with(id=self.fake_id)
        self.res.delete.assert_called_with(self.session)

        # Delete generally doesn't return anything, so we will normally
        # swallow any return from within a service's proxy, but make sure
        # we can still return for any cases where values are returned.
        self.res.delete.return_value = self.fake_id
        rv = self.sot._delete(DeleteableResource, self.fake_id)
        self.assertEqual(rv, self.fake_id)

    def test_delete_ignore_missing(self):
        self.res.delete.side_effect = exceptions.NotFoundException(
            message="test", http_status=404)

        rv = self.sot._delete(DeleteableResource, self.fake_id)
        self.assertIsNone(rv)

    def test_delete_ResourceNotFound(self):
        self.res.delete.side_effect = exceptions.NotFoundException(
            message="test", http_status=404)

        self.assertRaisesRegexp(
            exceptions.ResourceNotFound,
            "No %s found for %s" % (DeleteableResource.__name__, self.res),
            self.sot._delete, DeleteableResource, self.res,
            ignore_missing=False)

    def test_delete_HttpException(self):
        self.res.delete.side_effect = exceptions.HttpException(
            message="test", http_status=500)

        self.assertRaises(exceptions.HttpException, self.sot._delete,
                          DeleteableResource, self.res, ignore_missing=False)


class TestProxyUpdate(testtools.TestCase):

    def setUp(self):
        super(TestProxyUpdate, self).setUp()

        self.session = mock.Mock()

        self.fake_id = 1
        self.fake_result = "fake_result"

        self.res = mock.Mock(spec=UpdateableResource)
        self.res.update = mock.Mock(return_value=self.fake_result)
        self.res.update_attrs = mock.Mock()

        self.sot = proxy.BaseProxy(self.session)

        self.attrs = {"x": 1, "y": 2, "z": 3}

        UpdateableResource.existing = mock.Mock(return_value=self.res)

    def _test_update(self, value):
        rv = self.sot._update(UpdateableResource, value, **self.attrs)

        self.assertEqual(rv, self.fake_result)
        self.res.update_attrs.assert_called_once_with(self.attrs)
        self.res.update.assert_called_once_with(self.session)

    def test_update_resource(self):
        self._test_update(self.res)

    def test_update_id(self):
        self._test_update(self.fake_id)


class TestProxyCreate(testtools.TestCase):

    def setUp(self):
        super(TestProxyCreate, self).setUp()

        self.session = mock.Mock()

        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=CreateableResource)
        self.res.create = mock.Mock(return_value=self.fake_result)

        self.sot = proxy.BaseProxy(self.session)

    def test_create_attributes(self):
        CreateableResource.new = mock.Mock(return_value=self.res)

        attrs = {"x": 1, "y": 2, "z": 3}
        rv = self.sot._create(CreateableResource, **attrs)

        self.assertEqual(rv, self.fake_result)
        CreateableResource.new.assert_called_once_with(**attrs)
        self.res.create.assert_called_once_with(self.session)


class TestProxyGet(testtools.TestCase):

    def setUp(self):
        super(TestProxyGet, self).setUp()

        self.session = mock.Mock()

        self.fake_id = 1
        self.fake_name = "fake_name"
        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=RetrieveableResource)
        self.res.id = self.fake_id
        self.res.get = mock.Mock(return_value=self.fake_result)

        self.sot = proxy.BaseProxy(self.session)
        RetrieveableResource.existing = mock.Mock(return_value=self.res)

    def test_get_resource(self):
        rv = self.sot._get(RetrieveableResource, self.res)

        self.res.get.assert_called_with(self.session, args=None)
        self.assertEqual(rv, self.fake_result)

    def test_get_resource_with_args(self):
        rv = self.sot._get(RetrieveableResource, self.res, args={'K': 'V'})

        self.res.get.assert_called_with(self.session, args={'K': 'V'})
        self.assertEqual(rv, self.fake_result)

    def test_get_id(self):
        rv = self.sot._get(RetrieveableResource, self.fake_id)

        RetrieveableResource.existing.assert_called_with(id=self.fake_id)
        self.res.get.assert_called_with(self.session, args=None)
        self.assertEqual(rv, self.fake_result)

    def test_get_not_found(self):
        self.res.get.side_effect = exceptions.NotFoundException(
            message="test", http_status=404)

        self.assertRaisesRegexp(
            exceptions.ResourceNotFound,
            "No %s found for %s" % (RetrieveableResource.__name__, self.res),
            self.sot._get, RetrieveableResource, self.res)


class TestProxyList(testtools.TestCase):

    def setUp(self):
        super(TestProxyList, self).setUp()

        self.session = mock.Mock()

        self.fake_a = 1
        self.fake_b = 2
        self.fake_c = 3
        self.fake_resource = resource.Resource.new(id=self.fake_a)
        self.fake_response = [resource.Resource()]
        self.fake_query = {"a": self.fake_resource, "b": self.fake_b}
        self.fake_path_args = {"c": self.fake_c}

        self.sot = proxy.BaseProxy(self.session)
        ListableResource.list = mock.Mock()
        ListableResource.list.return_value = self.fake_response

    def _test_list(self, path_args, paginated, **query):
        rv = self.sot._list(ListableResource, path_args=path_args,
                            paginated=paginated, **query)

        self.assertEqual(self.fake_response, rv)
        ListableResource.list.assert_called_once_with(
            self.session, path_args=path_args, paginated=paginated,
            params={'a': self.fake_a, 'b': self.fake_b})

    def test_list_paginated(self):
        self._test_list(self.fake_path_args, True, **self.fake_query)

    def test_list_non_paginated(self):
        self._test_list(self.fake_path_args, False, **self.fake_query)


class TestProxyHead(testtools.TestCase):

    def setUp(self):
        super(TestProxyHead, self).setUp()

        self.session = mock.Mock()

        self.fake_id = 1
        self.fake_name = "fake_name"
        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=HeadableResource)
        self.res.id = self.fake_id
        self.res.head = mock.Mock(return_value=self.fake_result)

        self.sot = proxy.BaseProxy(self.session)
        HeadableResource.existing = mock.Mock(return_value=self.res)

    def test_head_resource(self):
        rv = self.sot._head(HeadableResource, self.res)

        self.res.head.assert_called_with(self.session)
        self.assertEqual(rv, self.fake_result)

    def test_head_id(self):
        rv = self.sot._head(HeadableResource, self.fake_id)

        HeadableResource.existing.assert_called_with(id=self.fake_id)
        self.res.head.assert_called_with(self.session)
        self.assertEqual(rv, self.fake_result)

    def test_head_no_value(self):
        MockHeadResource = mock.Mock(spec=HeadableResource)
        instance = mock.Mock()
        MockHeadResource.return_value = instance

        self.sot._head(MockHeadResource)

        MockHeadResource.assert_called_with()
        instance.head.assert_called_with(self.session)

    @mock.patch("openstack.resource.wait_for_status")
    def test_wait_for(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_status(mock_resource, 'ACTIVE')
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 'ACTIVE', [], 2, 120)

    @mock.patch("openstack.resource.wait_for_status")
    def test_wait_for_params(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_status(mock_resource, 'ACTIVE', ['ERROR'], 1, 2)
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 'ACTIVE', ['ERROR'], 1, 2)

    @mock.patch("openstack.resource.wait_for_delete")
    def test_wait_for_delete(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_delete(mock_resource)
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 2, 120)

    @mock.patch("openstack.resource.wait_for_delete")
    def test_wait_for_delete_params(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_delete(mock_resource, 1, 2)
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 1, 2)
