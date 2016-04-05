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
from openstack import proxy2
from openstack import resource2


class DeleteableResource(resource2.Resource):
    allow_delete = True


class UpdateableResource(resource2.Resource):
    allow_update = True


class CreateableResource(resource2.Resource):
    allow_create = True


class RetrieveableResource(resource2.Resource):
    allow_retrieve = True


class ListableResource(resource2.Resource):
    allow_list = True


class HeadableResource(resource2.Resource):
    allow_head = True


class TestProxyPrivate(testtools.TestCase):

    def setUp(self):
        super(TestProxyPrivate, self).setUp()

        def method(self, expected_type, value):
            return value

        self.sot = mock.Mock()
        self.sot.method = method

        self.fake_proxy = proxy2.BaseProxy("session")

    def _test_correct(self, value):
        decorated = proxy2._check_resource(strict=False)(self.sot.method)
        rv = decorated(self.sot, resource2.Resource, value)

        self.assertEqual(value, rv)

    def test__check_resource_correct_resource(self):
        res = resource2.Resource()
        self._test_correct(res)

    def test__check_resource_notstrict_id(self):
        self._test_correct("abc123-id")

    def test__check_resource_strict_id(self):
        decorated = proxy2._check_resource(strict=True)(self.sot.method)
        self.assertRaisesRegexp(ValueError, "A Resource must be passed",
                                decorated, self.sot, resource2.Resource,
                                "this-is-not-a-resource")

    def test__check_resource_incorrect_resource(self):
        class OneType(resource2.Resource):
            pass

        class AnotherType(resource2.Resource):
            pass

        value = AnotherType()
        decorated = proxy2._check_resource(strict=False)(self.sot.method)
        self.assertRaisesRegexp(ValueError,
                                "Expected OneType but received AnotherType",
                                decorated, self.sot, OneType, value)

    def test__get_uri_attribute_no_parent(self):
        class Child(resource2.Resource):
            something = resource2.Body("something")

        attr = "something"
        value = "nothing"
        child = Child(something=value)

        result = self.fake_proxy._get_uri_attribute(child, None, attr)

        self.assertEqual(value, result)

    def test__get_uri_attribute_with_parent(self):
        class Parent(resource2.Resource):
            pass

        value = "nothing"
        parent = Parent(id=value)

        result = self.fake_proxy._get_uri_attribute("child", parent, "attr")

        self.assertEqual(value, result)

    def test__get_resource_new(self):
        value = "hello"
        fake_type = mock.Mock(spec=resource2.Resource)
        fake_type.new = mock.Mock(return_value=value)
        attrs = {"first": "Brian", "last": "Curtin"}

        result = self.fake_proxy._get_resource(fake_type, None, **attrs)

        fake_type.new.assert_called_with(**attrs)
        self.assertEqual(value, result)

    def test__get_resource_from_id(self):
        id = "eye dee"
        value = "hello"
        attrs = {"first": "Brian", "last": "Curtin"}

        # The isinstance check needs to take a type, not an instance,
        # so the mock.assert_called_with method isn't helpful here since
        # we can't pass in a mocked object. This class is a crude version
        # of that same behavior to let us check that `new` gets
        # called with the expected arguments.

        class Fake(object):
            call = {}

            @classmethod
            def new(cls, **kwargs):
                cls.call = kwargs
                return value

        result = self.fake_proxy._get_resource(Fake, id, **attrs)

        self.assertDictEqual(dict(id=id, **attrs), Fake.call)
        self.assertEqual(value, result)

    def test__get_resource_from_resource(self):
        res = mock.Mock(spec=resource2.Resource)
        res._update = mock.Mock()

        attrs = {"first": "Brian", "last": "Curtin"}

        result = self.fake_proxy._get_resource(resource2.Resource,
                                               res, **attrs)

        res._update.assert_called_once_with(**attrs)
        self.assertEqual(result, res)


class TestProxyDelete(testtools.TestCase):

    def setUp(self):
        super(TestProxyDelete, self).setUp()

        self.session = mock.Mock()

        self.fake_id = 1
        self.res = mock.Mock(spec=DeleteableResource)
        self.res.id = self.fake_id
        self.res.delete = mock.Mock()

        self.sot = proxy2.BaseProxy(self.session)
        DeleteableResource.new = mock.Mock(return_value=self.res)

    def test_delete(self):
        self.sot._delete(DeleteableResource, self.res)
        self.res.delete.assert_called_with(self.session)

        self.sot._delete(DeleteableResource, self.fake_id)
        DeleteableResource.new.assert_called_with(id=self.fake_id)
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

        self.sot = proxy2.BaseProxy(self.session)

        self.attrs = {"x": 1, "y": 2, "z": 3}

        UpdateableResource.new = mock.Mock(return_value=self.res)

    def test_update_resource(self):
        rv = self.sot._update(UpdateableResource, self.res, **self.attrs)

        self.assertEqual(rv, self.fake_result)
        self.res._update.assert_called_once_with(**self.attrs)
        self.res.update.assert_called_once_with(self.session)

    def test_update_id(self):
        rv = self.sot._update(UpdateableResource, self.fake_id, **self.attrs)

        self.assertEqual(rv, self.fake_result)
        self.res.update.assert_called_once_with(self.session)


class TestProxyCreate(testtools.TestCase):

    def setUp(self):
        super(TestProxyCreate, self).setUp()

        self.session = mock.Mock()

        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=CreateableResource)
        self.res.create = mock.Mock(return_value=self.fake_result)

        self.sot = proxy2.BaseProxy(self.session)

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

        self.sot = proxy2.BaseProxy(self.session)
        RetrieveableResource.new = mock.Mock(return_value=self.res)

    def test_get_resource(self):
        rv = self.sot._get(RetrieveableResource, self.res)

        self.res.get.assert_called_with(self.session)
        self.assertEqual(rv, self.fake_result)

    def test_get_resource_with_args(self):
        args = {"key": "value"}
        rv = self.sot._get(RetrieveableResource, self.res, **args)

        self.res._update.assert_called_once_with(**args)
        self.res.get.assert_called_with(self.session)
        self.assertEqual(rv, self.fake_result)

    def test_get_id(self):
        rv = self.sot._get(RetrieveableResource, self.fake_id)

        RetrieveableResource.new.assert_called_with(id=self.fake_id)
        self.res.get.assert_called_with(self.session)
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

        self.args = {"a": "A", "b": "B", "c": "C"}
        self.fake_response = [resource2.Resource()]

        self.sot = proxy2.BaseProxy(self.session)
        ListableResource.list = mock.Mock()
        ListableResource.list.return_value = self.fake_response

    def _test_list(self, paginated):
        rv = self.sot._list(ListableResource, paginated=paginated, **self.args)

        self.assertEqual(self.fake_response, rv)
        ListableResource.list.assert_called_once_with(
            self.session, paginated=paginated, **self.args)

    def test_list_paginated(self):
        self._test_list(True)

    def test_list_non_paginated(self):
        self._test_list(False)


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

        self.sot = proxy2.BaseProxy(self.session)
        HeadableResource.new = mock.Mock(return_value=self.res)

    def test_head_resource(self):
        rv = self.sot._head(HeadableResource, self.res)

        self.res.head.assert_called_with(self.session)
        self.assertEqual(rv, self.fake_result)

    def test_head_id(self):
        rv = self.sot._head(HeadableResource, self.fake_id)

        HeadableResource.new.assert_called_with(id=self.fake_id)
        self.res.head.assert_called_with(self.session)
        self.assertEqual(rv, self.fake_result)


class TestProxyWaits(testtools.TestCase):

    def setUp(self):
        super(TestProxyWaits, self).setUp()

        self.session = mock.Mock()
        self.sot = proxy2.BaseProxy(self.session)

    @mock.patch("openstack.resource2.wait_for_status")
    def test_wait_for(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_status(mock_resource, 'ACTIVE')
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 'ACTIVE', [], 2, 120)

    @mock.patch("openstack.resource2.wait_for_status")
    def test_wait_for_params(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_status(mock_resource, 'ACTIVE', ['ERROR'], 1, 2)
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 'ACTIVE', ['ERROR'], 1, 2)

    @mock.patch("openstack.resource2.wait_for_delete")
    def test_wait_for_delete(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_delete(mock_resource)
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 2, 120)

    @mock.patch("openstack.resource2.wait_for_delete")
    def test_wait_for_delete_params(self, mock_wait):
        mock_resource = mock.Mock()
        mock_wait.return_value = mock_resource
        self.sot.wait_for_delete(mock_resource, 1, 2)
        mock_wait.assert_called_once_with(
            self.session, mock_resource, 1, 2)
