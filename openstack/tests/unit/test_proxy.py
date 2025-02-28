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

import copy
import queue
from unittest import mock

from keystoneauth1 import session
from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

from openstack import exceptions
from openstack import proxy
from openstack import resource
from openstack.tests.unit import base
from openstack.tests.unit import fakes
from openstack import utils


class DeleteableResource(resource.Resource):
    allow_delete = True


class UpdateableResource(resource.Resource):
    allow_commit = True


class CreateableResource(resource.Resource):
    allow_create = True


class RetrieveableResource(resource.Resource):
    allow_fetch = True


class ListableResource(resource.Resource):
    allow_list = True


class FilterableResource(resource.Resource):
    allow_list = True
    base_path = '/fakes'

    _query_mapping = resource.QueryParameters('a')
    a = resource.Body('a')
    b = resource.Body('b')
    c = resource.Body('c')


class HeadableResource(resource.Resource):
    allow_head = True


class TestProxyPrivate(base.TestCase):
    def setUp(self):
        super().setUp()

        def method(self, expected_type, value):
            return value

        self.sot = mock.Mock()
        self.sot.method = method

        self.session = mock.Mock()
        self.session._sdk_connection = self.cloud
        self.fake_proxy = proxy.Proxy(self.session)
        self.fake_proxy._connection = self.cloud

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

        class Fake:
            call = {}

            @classmethod
            def new(cls, **kwargs):
                cls.call = kwargs
                return value

        result = self.fake_proxy._get_resource(Fake, id, **attrs)

        self.assertDictEqual(
            dict(id=id, connection=mock.ANY, **attrs), Fake.call
        )
        self.assertEqual(value, result)

    def test__get_resource_from_resource(self):
        res = mock.Mock(spec=resource.Resource)
        res._update = mock.Mock()

        attrs = {"first": "Brian", "last": "Curtin"}

        result = self.fake_proxy._get_resource(resource.Resource, res, **attrs)

        res._update.assert_called_once_with(**attrs)
        self.assertEqual(result, res)

    def test__get_resource_from_munch(self):
        cls = mock.Mock()
        res = mock.Mock(spec=resource.Resource)
        res._update = mock.Mock()
        cls._from_munch.return_value = res

        m = utils.Munch(answer=42)
        attrs = {"first": "Brian", "last": "Curtin"}

        result = self.fake_proxy._get_resource(cls, m, **attrs)

        cls._from_munch.assert_called_once_with(m, connection=self.cloud)
        res._update.assert_called_once_with(**attrs)
        self.assertEqual(result, res)


class TestProxyDelete(base.TestCase):
    def setUp(self):
        super().setUp()

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
            connection=self.cloud, id=self.fake_id
        )
        self.res.delete.assert_called_with(self.sot)

        # Delete generally doesn't return anything, so we will normally
        # swallow any return from within a service's proxy, but make sure
        # we can still return for any cases where values are returned.
        self.res.delete.return_value = self.fake_id
        rv = self.sot._delete(DeleteableResource, self.fake_id)
        self.assertEqual(rv, self.fake_id)

    def test_delete_ignore_missing(self):
        self.res.delete.side_effect = exceptions.NotFoundException(
            message="test",
            response=fakes.FakeResponse(status_code=404, data={'error': None}),
        )

        rv = self.sot._delete(DeleteableResource, self.fake_id)
        self.assertIsNone(rv)

    def test_delete_NotFound(self):
        self.res.delete.side_effect = exceptions.NotFoundException(
            message="test",
            response=fakes.FakeResponse(status_code=404, data={'error': None}),
        )

        self.assertRaisesRegex(
            exceptions.NotFoundException,
            # TODO(shade) The mocks here are hiding the thing we want to test.
            "test",
            self.sot._delete,
            DeleteableResource,
            self.res,
            ignore_missing=False,
        )

    def test_delete_HttpException(self):
        self.res.delete.side_effect = exceptions.ResourceNotFound(
            message="test",
            response=fakes.FakeResponse(status_code=500, data={'error': None}),
        )

        self.assertRaises(
            exceptions.HttpException,
            self.sot._delete,
            DeleteableResource,
            self.res,
            ignore_missing=False,
        )


class TestProxyUpdate(base.TestCase):
    def setUp(self):
        super().setUp()

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
        rv = self.sot._update(
            UpdateableResource, self.res, base_path=base_path, **self.attrs
        )

        self.assertEqual(rv, self.fake_result)
        self.res._update.assert_called_once_with(**self.attrs)
        self.res.commit.assert_called_once_with(self.sot, base_path=base_path)

    def test_update_id(self):
        rv = self.sot._update(UpdateableResource, self.fake_id, **self.attrs)

        self.assertEqual(rv, self.fake_result)
        self.res.commit.assert_called_once_with(self.sot, base_path=None)


class TestProxyCreate(base.TestCase):
    def setUp(self):
        super().setUp()

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
            connection=self.cloud, **attrs
        )
        self.res.create.assert_called_once_with(self.sot, base_path=None)

    def test_create_attributes_override_base_path(self):
        CreateableResource.new = mock.Mock(return_value=self.res)

        base_path = 'dummy'
        attrs = {"x": 1, "y": 2, "z": 3}
        rv = self.sot._create(CreateableResource, base_path=base_path, **attrs)

        self.assertEqual(rv, self.fake_result)
        CreateableResource.new.assert_called_once_with(
            connection=self.cloud, **attrs
        )
        self.res.create.assert_called_once_with(self.sot, base_path=base_path)


class TestProxyBulkCreate(base.TestCase):
    def setUp(self):
        super().setUp()

        class Res(resource.Resource):
            pass

        self.session = mock.Mock()
        self.result = mock.sentinel
        self.data = mock.Mock()

        self.sot = proxy.Proxy(self.session)
        self.cls = Res
        self.cls.bulk_create = mock.Mock(return_value=self.result)

    def test_bulk_create_attributes(self):
        rv = self.sot._bulk_create(self.cls, self.data)

        self.assertEqual(rv, self.result)
        self.cls.bulk_create.assert_called_once_with(
            self.sot, self.data, base_path=None
        )

    def test_bulk_create_attributes_override_base_path(self):
        base_path = 'dummy'

        rv = self.sot._bulk_create(self.cls, self.data, base_path=base_path)

        self.assertEqual(rv, self.result)
        self.cls.bulk_create.assert_called_once_with(
            self.sot, self.data, base_path=base_path
        )


class TestProxyGet(base.TestCase):
    def setUp(self):
        super().setUp()

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
            self.sot,
            requires_id=True,
            base_path=None,
            skip_cache=mock.ANY,
            error_message=mock.ANY,
        )
        self.assertEqual(rv, self.fake_result)

    def test_get_resource_with_args(self):
        args = {"key": "value"}
        rv = self.sot._get(RetrieveableResource, self.res, **args)

        self.res._update.assert_called_once_with(**args)
        self.res.fetch.assert_called_with(
            self.sot,
            requires_id=True,
            base_path=None,
            skip_cache=mock.ANY,
            error_message=mock.ANY,
        )
        self.assertEqual(rv, self.fake_result)

    def test_get_id(self):
        rv = self.sot._get(RetrieveableResource, self.fake_id)

        RetrieveableResource.new.assert_called_with(
            connection=self.cloud, id=self.fake_id
        )
        self.res.fetch.assert_called_with(
            self.sot,
            requires_id=True,
            base_path=None,
            skip_cache=mock.ANY,
            error_message=mock.ANY,
        )
        self.assertEqual(rv, self.fake_result)

    def test_get_base_path(self):
        base_path = 'dummy'
        rv = self.sot._get(
            RetrieveableResource, self.fake_id, base_path=base_path
        )

        RetrieveableResource.new.assert_called_with(
            connection=self.cloud, id=self.fake_id
        )
        self.res.fetch.assert_called_with(
            self.sot,
            requires_id=True,
            base_path=base_path,
            skip_cache=mock.ANY,
            error_message=mock.ANY,
        )
        self.assertEqual(rv, self.fake_result)

    def test_get_not_found(self):
        self.res.fetch.side_effect = exceptions.NotFoundException(
            message="test",
            response=fakes.FakeResponse(status_code=404, data={'error': None}),
        )

        self.assertRaisesRegex(
            exceptions.NotFoundException,
            "test",
            self.sot._get,
            RetrieveableResource,
            self.res,
        )


class TestProxyList(base.TestCase):
    def setUp(self):
        super().setUp()

        self.session = mock.Mock()

        self.args = {"a": "A", "b": "B", "c": "C"}
        self.fake_response = [resource.Resource()]

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud
        ListableResource.list = mock.Mock()
        ListableResource.list.return_value = self.fake_response

    def _test_list(self, paginated, base_path=None):
        rv = self.sot._list(
            ListableResource,
            paginated=paginated,
            base_path=base_path,
            **self.args,
        )

        self.assertEqual(self.fake_response, rv)
        ListableResource.list.assert_called_once_with(
            self.sot, paginated=paginated, base_path=base_path, **self.args
        )

    def test_list_paginated(self):
        self._test_list(True)

    def test_list_non_paginated(self):
        self._test_list(False)

    def test_list_override_base_path(self):
        self._test_list(False, base_path='dummy')

    def test_list_filters_jmespath(self):
        fake_response = [
            FilterableResource(a='a1', b='b1', c='c'),
            FilterableResource(a='a2', b='b2', c='c'),
            FilterableResource(a='a3', b='b3', c='c'),
        ]
        FilterableResource.list = mock.Mock()
        FilterableResource.list.return_value = fake_response

        rv = self.sot._list(
            FilterableResource,
            paginated=False,
            base_path=None,
            jmespath_filters="[?c=='c']",
        )
        self.assertEqual(3, len(rv))

        # Test filtering based on unknown attribute
        rv = self.sot._list(
            FilterableResource,
            paginated=False,
            base_path=None,
            jmespath_filters="[?d=='c']",
        )
        self.assertEqual(0, len(rv))


class TestProxyHead(base.TestCase):
    def setUp(self):
        super().setUp()

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
            connection=self.cloud, id=self.fake_id
        )
        self.res.head.assert_called_with(self.sot, base_path=None)
        self.assertEqual(rv, self.fake_result)


class TestExtractName(base.TestCase):
    scenarios = [
        ('slash_servers_bare', dict(url='/servers', parts=['servers'])),
        ('slash_servers_arg', dict(url='/servers/1', parts=['server'])),
        ('servers_bare', dict(url='servers', parts=['servers'])),
        ('servers_arg', dict(url='servers/1', parts=['server'])),
        ('networks_bare', dict(url='/v2.0/networks', parts=['networks'])),
        ('networks_arg', dict(url='/v2.0/networks/1', parts=['network'])),
        ('tokens', dict(url='/v3/tokens', parts=['tokens'])),
        ('discovery', dict(url='/', parts=['discovery'])),
        (
            'secgroups',
            dict(
                url='/servers/1/os-security-groups',
                parts=['server', 'os-security-groups'],
            ),
        ),
        ('bm_chassis', dict(url='/v1/chassis/id', parts=['chassis'])),
    ]

    def test_extract_name(self):
        results = proxy.Proxy(mock.Mock())._extract_name(self.url)
        self.assertEqual(self.parts, results)


class TestProxyCache(base.TestCase):
    class Res(resource.Resource):
        base_path = 'fake'

        allow_commit = True
        allow_fetch = True

        foo = resource.Body('foo')

    def setUp(self):
        super().setUp(cloud_config_fixture='clouds_cache.yaml')

        self.session = mock.Mock(spec=session.Session)
        self.session._sdk_connection = self.cloud
        self.session.get_project_id = mock.Mock(return_value='fake_prj')

        self.response = mock.Mock()
        self.response.status_code = 200
        self.response.history = []
        self.response.headers = {}
        self.response.body = {}
        self.response.json = mock.Mock(return_value=self.response.body)
        self.session.request = mock.Mock(return_value=self.response)

        self.sot = proxy.Proxy(self.session)
        self.sot._connection = self.cloud
        self.sot.service_type = 'srv'

    def _get_key(self, id):
        return f"srv.fake.fake/{id}.{{'microversion': None, 'params': {{}}}}"

    def test_get_not_in_cache(self):
        self.cloud._cache_expirations['srv.fake'] = 5
        self.sot._get(self.Res, '1')

        self.session.request.assert_called_with(
            'fake/1',
            'GET',
            connect_retries=mock.ANY,
            raise_exc=mock.ANY,
            global_request_id=mock.ANY,
            microversion=mock.ANY,
            params=mock.ANY,
            endpoint_filter=mock.ANY,
            headers=mock.ANY,
            rate_semaphore=mock.ANY,
        )
        self.assertIn(self._get_key(1), self.cloud._api_cache_keys)

    def test_get_from_cache(self):
        key = self._get_key(2)

        self.cloud._cache.set(key, self.response)
        # set expiration for the resource to respect cache
        self.cloud._cache_expirations['srv.fake'] = 5

        self.sot._get(self.Res, '2')
        self.session.request.assert_not_called()

    def test_modify(self):
        key = self._get_key(3)

        self.cloud._cache.set(key, self.response)
        self.cloud._api_cache_keys.add(key)
        self.cloud._cache_expirations['srv.fake'] = 5

        # Ensure first call gets value from cache
        self.sot._get(self.Res, '3')
        self.session.request.assert_not_called()

        # update call invalidates the cache and triggers API
        rs = self.Res.existing(id='3')
        self.sot._update(self.Res, rs, foo='bar')

        self.session.request.assert_called()
        self.assertIsNotNone(self.cloud._cache.get(key))
        self.assertEqual('NoValue', type(self.cloud._cache.get(key)).__name__)
        self.assertNotIn(key, self.cloud._api_cache_keys)

        # next get call again triggers API
        self.sot._get(self.Res, '3')
        self.session.request.assert_called()

    def test_get_bypass_cache(self):
        key = self._get_key(4)

        resp = copy.deepcopy(self.response)
        resp.body = {'foo': 'bar'}
        self.cloud._api_cache_keys.add(key)
        self.cloud._cache.set(key, resp)
        # set expiration for the resource to respect cache
        self.cloud._cache_expirations['srv.fake'] = 5

        self.sot._get(self.Res, '4', skip_cache=True)
        self.session.request.assert_called()
        # validate we got empty body as expected, and not what is in cache
        self.assertEqual(dict(), self.response.body)
        self.assertNotIn(key, self.cloud._api_cache_keys)
        self.assertEqual('NoValue', type(self.cloud._cache.get(key)).__name__)


class TestProxyCleanup(base.TestCase):
    def setUp(self):
        super().setUp()

        self.session = mock.Mock()
        self.session._sdk_connection = self.cloud

        self.fake_id = 1
        self.fake_name = "fake_name"
        self.fake_result = "fake_result"
        self.res = mock.Mock(spec=resource.Resource)
        self.res.id = self.fake_id
        self.res.created_at = '2020-01-02T03:04:05'
        self.res.updated_at = '2020-01-03T03:04:05'
        self.res_no_updated = mock.Mock(spec=resource.Resource)
        self.res_no_updated.created_at = '2020-01-02T03:04:05'

        self.sot = proxy.Proxy(self.session)
        self.sot.service_type = "block-storage"

        self.delete_mock = mock.Mock()

    def test_filters_evaluation_created_at(self):
        self.assertTrue(
            self.sot._service_cleanup_resource_filters_evaluation(
                self.res, filters={'created_at': '2020-02-03T00:00:00'}
            )
        )

    def test_filters_evaluation_created_at_not(self):
        self.assertFalse(
            self.sot._service_cleanup_resource_filters_evaluation(
                self.res, filters={'created_at': '2020-01-01T00:00:00'}
            )
        )

    def test_filters_evaluation_updated_at(self):
        self.assertTrue(
            self.sot._service_cleanup_resource_filters_evaluation(
                self.res, filters={'updated_at': '2020-02-03T00:00:00'}
            )
        )

    def test_filters_evaluation_updated_at_not(self):
        self.assertFalse(
            self.sot._service_cleanup_resource_filters_evaluation(
                self.res, filters={'updated_at': '2020-01-01T00:00:00'}
            )
        )

    def test_filters_evaluation_updated_at_missing(self):
        self.assertFalse(
            self.sot._service_cleanup_resource_filters_evaluation(
                self.res_no_updated,
                filters={'updated_at': '2020-01-01T00:00:00'},
            )
        )

    def test_filters_empty(self):
        self.assertTrue(
            self.sot._service_cleanup_resource_filters_evaluation(
                self.res_no_updated
            )
        )

    def test_service_cleanup_dry_run(self):
        self.assertTrue(
            self.sot._service_cleanup_del_res(
                self.delete_mock, self.res, dry_run=True
            )
        )
        self.delete_mock.assert_not_called()

    def test_service_cleanup_dry_run_default(self):
        self.assertTrue(
            self.sot._service_cleanup_del_res(self.delete_mock, self.res)
        )
        self.delete_mock.assert_not_called()

    def test_service_cleanup_real_run(self):
        self.assertTrue(
            self.sot._service_cleanup_del_res(
                self.delete_mock,
                self.res,
                dry_run=False,
            )
        )
        self.delete_mock.assert_called_with(self.res)

    def test_service_cleanup_real_run_identified_resources(self):
        rd = dict()
        self.assertTrue(
            self.sot._service_cleanup_del_res(
                self.delete_mock,
                self.res,
                dry_run=False,
                identified_resources=rd,
            )
        )
        self.delete_mock.assert_called_with(self.res)
        self.assertEqual(self.res, rd[self.res.id])

    def test_service_cleanup_resource_evaluation_false(self):
        self.assertFalse(
            self.sot._service_cleanup_del_res(
                self.delete_mock,
                self.res,
                dry_run=False,
                resource_evaluation_fn=lambda x, y, z: False,
            )
        )
        self.delete_mock.assert_not_called()

    def test_service_cleanup_resource_evaluation_true(self):
        self.assertTrue(
            self.sot._service_cleanup_del_res(
                self.delete_mock,
                self.res,
                dry_run=False,
                resource_evaluation_fn=lambda x, y, z: True,
            )
        )
        self.delete_mock.assert_called()

    def test_service_cleanup_resource_evaluation_override_filters(self):
        self.assertFalse(
            self.sot._service_cleanup_del_res(
                self.delete_mock,
                self.res,
                dry_run=False,
                resource_evaluation_fn=lambda x, y, z: False,
                filters={'created_at': '2200-01-01'},
            )
        )

    def test_service_cleanup_filters(self):
        self.assertTrue(
            self.sot._service_cleanup_del_res(
                self.delete_mock,
                self.res,
                dry_run=False,
                filters={'created_at': '2200-01-01'},
            )
        )
        self.delete_mock.assert_called()

    def test_service_cleanup_queue(self):
        q = queue.Queue()
        self.assertTrue(
            self.sot._service_cleanup_del_res(
                self.delete_mock,
                self.res,
                dry_run=False,
                client_status_queue=q,
                filters={'created_at': '2200-01-01'},
            )
        )
        self.assertEqual(self.res, q.get_nowait())

    def test_should_skip_resource_cleanup(self):
        excluded = ["block_storage.backup"]
        self.assertTrue(
            self.sot.should_skip_resource_cleanup("backup", excluded)
        )
        self.assertFalse(
            self.sot.should_skip_resource_cleanup("volume", excluded)
        )
