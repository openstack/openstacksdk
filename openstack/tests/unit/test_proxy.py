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
import munch
from openstack.tests.unit import base

from openstack import exceptions
from openstack import proxy
from openstack import resource


class DeleteableResource(resource.Resource):
    allow_delete = True


class UpdateableResource(resource.Resource):
    allow_commit = True


class CreateableResource(resource.Resource):
    allow_create = True


class RetrieveableResource(resource.Resource):
    allow_retrieve = True


class ListableResource(resource.Resource):
    allow_list = True


class HeadableResource(resource.Resource):
    allow_head = True


class TestProxyPrivate(base.TestCase):

    def setUp(self):
        super(TestProxyPrivate, self).setUp()

        def method(self, expected_type, value):
            return value

        self.sot = mock.Mock()
        self.sot.method = method

        self.session = mock.Mock()
        self.session._sdk_connection = self.cloud
        self.fake_proxy = proxy.Proxy(self.session)
        self.fake_proxy._connection = self.cloud

    def _test_correct(self, value):
        decorated = proxy._check_resource(strict=False)(self.sot.method)
        rv = decorated(self.sot, resource.Resource, value)

        self.assertEqual(value, rv)

    def test__check_resource_correct_resource(self):
        res = resource.Resource()
        self._test_correct(res)

    def test__check_resource_notstrict_id(self):
        self._test_correct("abc123-id")

    def test__check_resource_strict_id(self):
        decorated = proxy._check_resource(strict=True)(self.sot.method)
        self.assertRaisesRegex(ValueError, "A Resource must be passed",
                               decorated, self.sot, resource.Resource,
                               "this-is-not-a-resource")

    def test__check_resource_incorrect_resource(self):
        class OneType(resource.Resource):
            pass

        class AnotherType(resource.Resource):
            pass

        value = AnotherType()
        decorated = proxy._check_resource(strict=False)(self.sot.method)
        self.assertRaisesRegex(ValueError,
                               "Expected OneType but received AnotherType",
                               decorated, self.sot, OneType, value)

    def test__get_uri_attribute_no_parent(self):
        class Child(resource.Resource):
            something = resource.Body("something")

        attr = "something"
        value = "nothing"
        child = Child(something=value)

        result = self.fake_proxy._get_uri_attribute(child, None, attr)

        self.assertEqual(value, result)

    def test__get_uri_attribute_with_parent(self):
        class Parent(resource.Resource):
            pass

        value = "nothing"
        parent = Parent(id=value)

        result = self.fake_proxy._get_uri_attribute("child", parent, "attr")

        self.assertEqual(value, result)

    def test__get_resource_new(self):
        value = "hello"
        fake_type = mock.Mock(spec=resource.Resource)
        fake_type.new = mock.Mock(return_value=value)
        attrs = {"first": "Brian", "last": "Curtin"}

        result = self.fake_proxy._get_resource(fake_type, None, **attrs)

        fake_type.new.assert_called_with(connection=self.cloud, **attrs)
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

        self.assertDictEqual(
            dict(id=id, connection=mock.ANY, **attrs), Fake.call)
        self.assertEqual(value, result)

    def test__get_resource_from_resource(self):
        res = mock.Mock(spec=resource.Resource)
        res._update = mock.Mock()

        attrs = {"first": "Brian", "last": "Curtin"}

        result = self.fake_proxy._get_resource(resource.Resource,
                                               res, **attrs)

        res._update.assert_called_once_with(**attrs)
        self.assertEqual(result, res)

    def test__get_resource_from_munch(self):
        cls = mock.Mock()
        res = mock.Mock(spec=resource.Resource)
        res._update = mock.Mock()
        cls._from_munch.return_value = res

        m = munch.Munch(answer=42)
        attrs = {"first": "Brian", "last": "Curtin"}

        result = self.fake_proxy._get_resource(cls, m, **attrs)

        cls._from_munch.assert_called_once_with(m, connection=self.cloud)
        res._update.assert_called_once_with(**attrs)
        self.assertEqual(result, res)


class TestProxyDelete(base.TestCase):

    def setUp(self):
        super(TestProxyDelete, self).setUp()

        self.session = mock.Mock()
        self.session._sdk_connection = self.cloud

        self.fake_id = 1
        self.res = mock.Mock(spec=DeleteableResource)
        self.res.id = self.fake_id
        self.res.delete = mock.Mock()

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud
        DeleteableResource.new = mock.Mock(return_value=self.res)

    def test_delete(self):
        self.sot._delete(DeleteableResource, self.res)
        self.res.delete.assert_called_with(self.sot)

        self.sot._delete(DeleteableResource, self.fake_id)
        DeleteableResource.new.assert_called_with(
            connection=self.cloud, id=self.fake_id)
        self.res.delete.assert_called_with(self.sot)

        # Delete generally doesn't return anything, so we will normally
        # swallow any return from within a service's proxy, but make sure
        # we can still return for any cases where values are returned.
        self.res.delete.return_value = self.fake_id
        rv = self.sot._delete(DeleteableResource, self.fake_id)
        self.assertEqual(rv, self.fake_id)

    def test_delete_ignore_missing(self):
        self.res.delete.side_effect = exceptions.ResourceNotFound(
            message="test", http_status=404)

        rv = self.sot._delete(DeleteableResource, self.fake_id)
        self.assertIsNone(rv)

    def test_delete_NotFound(self):
        self.res.delete.side_effect = exceptions.ResourceNotFound(
            message="test", http_status=404)

        self.assertRaisesRegex(
            exceptions.ResourceNotFound,
            # TODO(shade) The mocks here are hiding the thing we want to test.
            "test",
            self.sot._delete, DeleteableResource, self.res,
            ignore_missing=False)

    def test_delete_HttpException(self):
        self.res.delete.side_effect = exceptions.HttpException(
            message="test", http_status=500)

        self.assertRaises(exceptions.HttpException, self.sot._delete,
                          DeleteableResource, self.res, ignore_missing=False)


class TestProxyUpdate(base.TestCase):

    def setUp(self):
        super(TestProxyUpdate, self).setUp()

        self.session = mock.Mock()

        self.fake_id = 1
        self.fake_result = "fake_result"

        self.res = mock.Mock(spec=UpdateableResource)
        self.res.commit = mock.Mock(return_value=self.fake_result)

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud

        self.attrs = {"x": 1, "y": 2, "z": 3}

        UpdateableResource.new = mock.Mock(return_value=self.res)

    def test_update_resource(self):
        rv = self.sot._update(UpdateableResource, self.res, **self.attrs)

        self.assertEqual(rv, self.fake_result)
        self.res._update.assert_called_once_with(**self.attrs)
        self.res.commit.assert_called_once_with(self.sot, base_path=None)

    def test_update_resource_override_base_path(self):
        base_path = 'dummy'
        rv = self.sot._update(UpdateableResource, self.res,
                              base_path=base_path, **self.attrs)

        self.assertEqual(rv, self.fake_result)
        self.res._update.assert_called_once_with(**self.attrs)
        self.res.commit.assert_called_once_with(self.sot, base_path=base_path)

    def test_update_id(self):
        rv = self.sot._update(UpdateableResource, self.fake_id, **self.attrs)

        self.assertEqual(rv, self.fake_result)
        self.res.commit.assert_called_once_with(self.sot, base_path=None)


class TestProxyCreate(base.TestCase):

    def setUp(self):
        super(TestProxyCreate, self).setUp()

        self.session = mock.Mock()
        self.session._sdk_connection = self.cloud

        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=CreateableResource)
        self.res.create = mock.Mock(return_value=self.fake_result)

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud

    def test_create_attributes(self):
        CreateableResource.new = mock.Mock(return_value=self.res)

        attrs = {"x": 1, "y": 2, "z": 3}
        rv = self.sot._create(CreateableResource, **attrs)

        self.assertEqual(rv, self.fake_result)
        CreateableResource.new.assert_called_once_with(
            connection=self.cloud, **attrs)
        self.res.create.assert_called_once_with(self.sot, base_path=None)

    def test_create_attributes_override_base_path(self):
        CreateableResource.new = mock.Mock(return_value=self.res)

        base_path = 'dummy'
        attrs = {"x": 1, "y": 2, "z": 3}
        rv = self.sot._create(CreateableResource, base_path=base_path, **attrs)

        self.assertEqual(rv, self.fake_result)
        CreateableResource.new.assert_called_once_with(
            connection=self.cloud, **attrs)
        self.res.create.assert_called_once_with(self.sot, base_path=base_path)


class TestProxyGet(base.TestCase):

    def setUp(self):
        super(TestProxyGet, self).setUp()

        self.session = mock.Mock()
        self.session._sdk_connection = self.cloud

        self.fake_id = 1
        self.fake_name = "fake_name"
        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=RetrieveableResource)
        self.res.id = self.fake_id
        self.res.fetch = mock.Mock(return_value=self.fake_result)

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud
        RetrieveableResource.new = mock.Mock(return_value=self.res)

    def test_get_resource(self):
        rv = self.sot._get(RetrieveableResource, self.res)

        self.res.fetch.assert_called_with(
            self.sot, requires_id=True,
            base_path=None,
            error_message=mock.ANY)
        self.assertEqual(rv, self.fake_result)

    def test_get_resource_with_args(self):
        args = {"key": "value"}
        rv = self.sot._get(RetrieveableResource, self.res, **args)

        self.res._update.assert_called_once_with(**args)
        self.res.fetch.assert_called_with(
            self.sot, requires_id=True, base_path=None,
            error_message=mock.ANY)
        self.assertEqual(rv, self.fake_result)

    def test_get_id(self):
        rv = self.sot._get(RetrieveableResource, self.fake_id)

        RetrieveableResource.new.assert_called_with(
            connection=self.cloud, id=self.fake_id)
        self.res.fetch.assert_called_with(
            self.sot, requires_id=True, base_path=None,
            error_message=mock.ANY)
        self.assertEqual(rv, self.fake_result)

    def test_get_base_path(self):
        base_path = 'dummy'
        rv = self.sot._get(RetrieveableResource, self.fake_id,
                           base_path=base_path)

        RetrieveableResource.new.assert_called_with(
            connection=self.cloud, id=self.fake_id)
        self.res.fetch.assert_called_with(
            self.sot, requires_id=True, base_path=base_path,
            error_message=mock.ANY)
        self.assertEqual(rv, self.fake_result)

    def test_get_not_found(self):
        self.res.fetch.side_effect = exceptions.ResourceNotFound(
            message="test", http_status=404)

        self.assertRaisesRegex(
            exceptions.ResourceNotFound,
            "test", self.sot._get, RetrieveableResource, self.res)


class TestProxyList(base.TestCase):

    def setUp(self):
        super(TestProxyList, self).setUp()

        self.session = mock.Mock()

        self.args = {"a": "A", "b": "B", "c": "C"}
        self.fake_response = [resource.Resource()]

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud
        ListableResource.list = mock.Mock()
        ListableResource.list.return_value = self.fake_response

    def _test_list(self, paginated, base_path=None):
        rv = self.sot._list(ListableResource, paginated=paginated,
                            base_path=base_path, **self.args)

        self.assertEqual(self.fake_response, rv)
        ListableResource.list.assert_called_once_with(
            self.sot, paginated=paginated, base_path=base_path, **self.args)

    def test_list_paginated(self):
        self._test_list(True)

    def test_list_non_paginated(self):
        self._test_list(False)

    def test_list_override_base_path(self):
        self._test_list(False, base_path='dummy')


class TestProxyHead(base.TestCase):

    def setUp(self):
        super(TestProxyHead, self).setUp()

        self.session = mock.Mock()
        self.session._sdk_connection = self.cloud

        self.fake_id = 1
        self.fake_name = "fake_name"
        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=HeadableResource)
        self.res.id = self.fake_id
        self.res.head = mock.Mock(return_value=self.fake_result)

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud
        HeadableResource.new = mock.Mock(return_value=self.res)

    def test_head_resource(self):
        rv = self.sot._head(HeadableResource, self.res)

        self.res.head.assert_called_with(self.sot, base_path=None)
        self.assertEqual(rv, self.fake_result)

    def test_head_resource_base_path(self):
        base_path = 'dummy'
        rv = self.sot._head(HeadableResource, self.res, base_path=base_path)

        self.res.head.assert_called_with(self.sot, base_path=base_path)
        self.assertEqual(rv, self.fake_result)

    def test_head_id(self):
        rv = self.sot._head(HeadableResource, self.fake_id)

        HeadableResource.new.assert_called_with(
            connection=self.cloud, id=self.fake_id)
        self.res.head.assert_called_with(self.sot, base_path=None)
        self.assertEqual(rv, self.fake_result)
