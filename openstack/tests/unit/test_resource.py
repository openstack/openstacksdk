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
import json
import os

from keystoneauth1 import session
import mock
import requests
from testtools import matchers

from openstack import exceptions
from openstack import format
from openstack import resource
from openstack.tests.unit import base
from openstack import utils


fake_parent = 'robert'
fake_name = 'rey'
fake_id = 99
fake_attr1 = 'lana'
fake_attr2 = 'del'

fake_resource = 'fake'
fake_resources = 'fakes'
fake_arguments = {'parent_name': fake_parent}
fake_base_path = '/fakes/%(parent_name)s/data'
fake_path = '/fakes/rey/data'

fake_data = {'id': fake_id,
             'enabled': True,
             'name': fake_name,
             'parent': fake_parent,
             'attr1': fake_attr1,
             'attr2': fake_attr2,
             'status': None}
fake_body = {fake_resource: fake_data}


class FakeParent(resource.Resource):
    id_attribute = "name"
    name = resource.prop('name')


class FakeResource(resource.Resource):

    resource_key = fake_resource
    resources_key = fake_resources
    base_path = fake_base_path

    allow_create = allow_retrieve = allow_update = True
    allow_delete = allow_list = allow_head = True

    enabled = resource.prop('enabled', type=format.BoolStr)
    name = resource.prop('name')
    parent = resource.prop('parent_name')
    first = resource.prop('attr1')
    second = resource.prop('attr2')
    third = resource.prop('attr3', alias='attr_three')
    status = resource.prop('status')


class FakeResourceNoKeys(FakeResource):

    resource_key = None
    resources_key = None


class PropTests(base.TestCase):

    def test_with_alias_and_type(self):
        class Test(resource.Resource):
            attr = resource.prop("attr1", alias="attr2", type=bool)

        t = Test(attrs={"attr2": 500})

        # Don't test with assertTrue because 500 evaluates to True.
        # Need to test that bool(500) happened and attr2 *is* True.
        self.assertIs(t.attr, True)

    def test_defaults(self):
        new_default = "new_default"

        class Test(resource.Resource):
            attr1 = resource.prop("attr1")
            attr2 = resource.prop("attr2", default=new_default)

        t = Test()

        self.assertIsNone(t.attr1)
        self.assertEqual(new_default, t.attr2)

        # When the default value is passed in, it is left untouched.
        # Check that attr2 is literally the same object we set as default.
        t.attr2 = new_default
        self.assertIs(new_default, t.attr2)

        not_default = 'not default'
        t2 = Test({'attr2': not_default})
        self.assertEqual(not_default, t2.attr2)

        # Assert that if the default is passed in, it overrides the previously
        # set value (bug #1425996)
        t2.attr2 = new_default
        self.assertEqual(new_default, t2.attr2)

    def test_get_without_instance(self):
        self.assertIsNone(FakeResource.name)

    def test_set_ValueError(self):
        class Test(resource.Resource):
            attr = resource.prop("attr", type=int)

        t = Test()

        def should_raise():
            t.attr = "this is not an int"

        self.assertThat(should_raise, matchers.raises(ValueError))

    def test_set_TypeError(self):
        class Type(object):
            def __init__(self):
                pass

        class Test(resource.Resource):
            attr = resource.prop("attr", type=Type)

        t = Test()

        def should_raise():
            t.attr = "this type takes no args"

        self.assertThat(should_raise, matchers.raises(TypeError))

    def test_resource_type(self):
        class FakestResource(resource.Resource):
            shortstop = resource.prop("shortstop", type=FakeResource)
            third_base = resource.prop("third_base", type=FakeResource)

        sot = FakestResource()
        id1 = "Ernie Banks"
        id2 = "Ron Santo"
        sot.shortstop = id1
        sot.third_base = id2

        resource1 = FakeResource.new(id=id1)
        self.assertEqual(resource1, sot.shortstop)
        self.assertEqual(id1, sot.shortstop.id)
        self.assertEqual(FakeResource, type(sot.shortstop))

        resource2 = FakeResource.new(id=id2)
        self.assertEqual(resource2, sot.third_base)
        self.assertEqual(id2, sot.third_base.id)
        self.assertEqual(FakeResource, type(sot.third_base))

        sot2 = FakestResource()
        sot2.shortstop = resource1
        sot2.third_base = resource2
        self.assertEqual(resource1, sot2.shortstop)
        self.assertEqual(id1, sot2.shortstop.id)
        self.assertEqual(FakeResource, type(sot2.shortstop))
        self.assertEqual(resource2, sot2.third_base)
        self.assertEqual(id2, sot2.third_base.id)
        self.assertEqual(FakeResource, type(sot2.third_base))

        body = {
            "shortstop": id1,
            "third_base": id2
        }
        sot3 = FakestResource(body)
        self.assertEqual(FakeResource({"id": id1}), sot3.shortstop)
        self.assertEqual(FakeResource({"id": id2}), sot3.third_base)

    def test_set_alias_same_name(self):
        class Test(resource.Resource):
            attr = resource.prop("something", alias="attr")

        val = "hey"
        args = {"something": val}
        sot = Test(args)

        self.assertEqual(val, sot._attrs["something"])
        self.assertEqual(val, sot.attr)

    def test_property_is_none(self):
        class Test(resource.Resource):
            attr = resource.prop("something", type=dict)

        args = {"something": None}
        sot = Test(args)

        self.assertIsNone(sot._attrs["something"])
        self.assertIsNone(sot.attr)


class HeaderTests(base.TestCase):
    class Test(resource.Resource):
        base_path = "/ramones"
        service = "punk"
        allow_create = True
        allow_update = True
        hey = resource.header("vocals")
        ho = resource.header("guitar")
        letsgo = resource.header("bass")

    def test_get(self):
        val = "joey"
        args = {"vocals": val}
        sot = HeaderTests.Test({'headers': args})
        self.assertEqual(val, sot.hey)
        self.assertIsNone(sot.ho)
        self.assertIsNone(sot.letsgo)

    def test_set_new(self):
        args = {"vocals": "joey", "bass": "deedee"}
        sot = HeaderTests.Test({'headers': args})
        sot._reset_dirty()
        sot.ho = "johnny"
        self.assertEqual("johnny", sot.ho)
        self.assertTrue(sot.is_dirty)

    def test_set_old(self):
        args = {"vocals": "joey", "bass": "deedee"}
        sot = HeaderTests.Test({'headers': args})
        sot._reset_dirty()
        sot.letsgo = "cj"
        self.assertEqual("cj", sot.letsgo)
        self.assertTrue(sot.is_dirty)

    def test_set_brand_new(self):
        sot = HeaderTests.Test({'headers': {}})
        sot._reset_dirty()
        sot.ho = "johnny"
        self.assertEqual("johnny", sot.ho)
        self.assertTrue(sot.is_dirty)
        self.assertEqual({'headers': {"guitar": "johnny"}}, sot)

    def test_1428342(self):
        sot = HeaderTests.Test({'headers':
                               requests.structures.CaseInsensitiveDict()})

        self.assertIsNone(sot.hey)

    def test_create_update_headers(self):
        sot = HeaderTests.Test()
        sot._reset_dirty()
        sot.ho = "johnny"
        sot.letsgo = "deedee"
        response = mock.Mock()
        response_body = {'id': 1}
        response.json = mock.Mock(return_value=response_body)
        response.headers = None
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=response)
        sess.put = mock.Mock(return_value=response)

        sot.create(sess)
        headers = {'guitar': 'johnny', 'bass': 'deedee'}
        sess.post.assert_called_with(HeaderTests.Test.base_path,
                                     endpoint_filter=HeaderTests.Test.service,
                                     headers=headers,
                                     json={})

        sot['id'] = 1
        sot.letsgo = "cj"
        headers = {'guitar': 'johnny', 'bass': 'cj'}
        sot.update(sess)
        sess.put.assert_called_with('ramones/1',
                                    endpoint_filter=HeaderTests.Test.service,
                                    headers=headers,
                                    json={})


class ResourceTests(base.TestCase):

    def setUp(self):
        super(ResourceTests, self).setUp()
        self.session = mock.Mock(spec=session.Session)
        self.session.get_filter = mock.Mock(return_value={})

    def assertCalledURL(self, method, url):
        # call_args gives a tuple of *args and tuple of **kwargs.
        # Check that the first arg in *args (the URL) has our url.
        self.assertEqual(method.call_args[0][0], url)

    def test_empty_id(self):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=fake_body)
        self.session.get.return_value = resp

        obj = FakeResource.new(**fake_arguments)
        self.assertEqual(obj, obj.get(self.session))

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    def test_not_allowed(self):
        class Nope(resource.Resource):
            allow_create = allow_retrieve = allow_update = False
            allow_delete = allow_list = allow_head = False

        nope = Nope()

        def cant_create():
            nope.create_by_id(1, 2)

        def cant_retrieve():
            nope.get_data_by_id(1, 2)

        def cant_update():
            nope.update_by_id(1, 2, 3)

        def cant_delete():
            nope.delete_by_id(1, 2)

        def cant_list():
            for i in nope.list(1):
                pass

        def cant_head():
            nope.head_data_by_id(1, 2)

        self.assertThat(cant_create,
                        matchers.raises(exceptions.MethodNotSupported))
        self.assertThat(cant_retrieve,
                        matchers.raises(exceptions.MethodNotSupported))
        self.assertThat(cant_update,
                        matchers.raises(exceptions.MethodNotSupported))
        self.assertThat(cant_delete,
                        matchers.raises(exceptions.MethodNotSupported))
        self.assertThat(cant_list,
                        matchers.raises(exceptions.MethodNotSupported))
        self.assertThat(cant_head,
                        matchers.raises(exceptions.MethodNotSupported))

    def _test_create_by_id(self, key, response_value, response_body,
                           attrs, json_body, response_headers=None):

        class FakeResource2(FakeResource):
            resource_key = key
            service = "my_service"

        response = mock.Mock()
        response.json = mock.Mock(return_value=response_body)
        response.headers = response_headers
        expected_resp = response_value.copy()
        if response_headers:
            expected_resp.update({'headers': response_headers})

        sess = mock.Mock()
        sess.put = mock.Mock(return_value=response)
        sess.post = mock.Mock(return_value=response)

        resp = FakeResource2.create_by_id(sess, attrs)
        self.assertEqual(expected_resp, resp)
        sess.post.assert_called_with(FakeResource2.base_path,
                                     endpoint_filter=FakeResource2.service,
                                     json=json_body)

        r_id = "my_id"
        resp = FakeResource2.create_by_id(sess, attrs, resource_id=r_id)
        self.assertEqual(response_value, resp)
        sess.put.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            endpoint_filter=FakeResource2.service,
            json=json_body)

        path_args = {"parent_name": "my_name"}
        resp = FakeResource2.create_by_id(sess, attrs, path_args=path_args)
        self.assertEqual(response_value, resp)
        sess.post.assert_called_with(FakeResource2.base_path % path_args,
                                     endpoint_filter=FakeResource2.service,
                                     json=json_body)

        resp = FakeResource2.create_by_id(sess, attrs, resource_id=r_id,
                                          path_args=path_args)
        self.assertEqual(response_value, resp)
        sess.put.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            endpoint_filter=FakeResource2.service,
            json=json_body)

    def test_create_without_resource_key(self):
        key = None
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = response_value
        attrs = response_value
        json_body = attrs
        self._test_create_by_id(key, response_value, response_body,
                                attrs, json_body)

    def test_create_with_response_headers(self):
        key = None
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = response_value
        response_headers = {'location': 'foo'}
        attrs = response_value.copy()
        json_body = attrs
        self._test_create_by_id(key, response_value, response_body,
                                attrs, json_body,
                                response_headers=response_headers)

    def test_create_with_resource_key(self):
        key = "my_key"
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = {key: response_value}
        attrs = response_body
        json_body = {key: attrs}
        self._test_create_by_id(key, response_value, response_body,
                                attrs, json_body)

    def _test_get_data_by_id(self, key, response_value, response_body):
        class FakeResource2(FakeResource):
            resource_key = key
            service = "my_service"

        response = mock.Mock()
        response.json = mock.Mock(return_value=response_body)

        sess = mock.Mock()
        sess.get = mock.Mock(return_value=response)

        r_id = "my_id"
        resp = FakeResource2.get_data_by_id(sess, resource_id=r_id)
        self.assertEqual(response_value, resp)
        sess.get.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            endpoint_filter=FakeResource2.service)

        path_args = {"parent_name": "my_name"}
        resp = FakeResource2.get_data_by_id(sess, resource_id=r_id,
                                            path_args=path_args)
        self.assertEqual(response_value, resp)
        sess.get.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            endpoint_filter=FakeResource2.service)

    def test_get_data_without_resource_key(self):
        key = None
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = response_value
        self._test_get_data_by_id(key, response_value, response_body)

    def test_get_data_with_resource_key(self):
        key = "my_key"
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = {key: response_value}
        self._test_get_data_by_id(key, response_value, response_body)

    def _test_head_data_by_id(self, key, response_value):
        class FakeResource2(FakeResource):
            resource_key = key
            service = "my_service"

        response = mock.Mock()
        response.headers = response_value

        sess = mock.Mock()
        sess.head = mock.Mock(return_value=response)

        r_id = "my_id"
        resp = FakeResource2.head_data_by_id(sess, resource_id=r_id)
        self.assertEqual({'headers': response_value}, resp)
        headers = {'Accept': ''}
        sess.head.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            endpoint_filter=FakeResource2.service,
            headers=headers)

        path_args = {"parent_name": "my_name"}
        resp = FakeResource2.head_data_by_id(sess, resource_id=r_id,
                                             path_args=path_args)
        self.assertEqual({'headers': response_value}, resp)
        headers = {'Accept': ''}
        sess.head.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            endpoint_filter=FakeResource2.service,
            headers=headers)

    def test_head_data_without_resource_key(self):
        key = None
        response_value = {"key1": "value1", "key2": "value2"}
        self._test_head_data_by_id(key, response_value)

    def test_head_data_with_resource_key(self):
        key = "my_key"
        response_value = {"key1": "value1", "key2": "value2"}
        self._test_head_data_by_id(key, response_value)

    def _test_update_by_id(self, key, response_value, response_body,
                           attrs, json_body, response_headers=None):

        class FakeResource2(FakeResource):
            patch_update = True
            resource_key = key
            service = "my_service"

        response = mock.Mock()
        response.json = mock.Mock(return_value=response_body)
        response.headers = response_headers
        expected_resp = response_value.copy()
        if response_headers:
            expected_resp.update({'headers': response_headers})

        sess = mock.Mock()
        sess.patch = mock.Mock(return_value=response)

        r_id = "my_id"
        resp = FakeResource2.update_by_id(sess, r_id, attrs)
        self.assertEqual(expected_resp, resp)
        sess.patch.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            endpoint_filter=FakeResource2.service,
            json=json_body)

        path_args = {"parent_name": "my_name"}
        resp = FakeResource2.update_by_id(sess, r_id, attrs,
                                          path_args=path_args)
        self.assertEqual(expected_resp, resp)
        sess.patch.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            endpoint_filter=FakeResource2.service,
            json=json_body)

    def test_update_without_resource_key(self):
        key = None
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = response_value
        attrs = response_value
        json_body = attrs
        self._test_update_by_id(key, response_value, response_body,
                                attrs, json_body)

    def test_update_with_resource_key(self):
        key = "my_key"
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = {key: response_value}
        attrs = response_value
        json_body = {key: attrs}
        self._test_update_by_id(key, response_value, response_body,
                                attrs, json_body)

    def test_update_with_response_headers(self):
        key = "my_key"
        response_value = {"a": 1, "b": 2, "c": 3}
        response_body = {key: response_value}
        response_headers = {'location': 'foo'}
        attrs = response_value.copy()
        json_body = {key: attrs}
        self._test_update_by_id(key, response_value, response_body,
                                attrs, json_body,
                                response_headers=response_headers)

    def test_delete_by_id(self):
        class FakeResource2(FakeResource):
            service = "my_service"

        sess = mock.Mock()
        sess.delete = mock.Mock(return_value=None)

        r_id = "my_id"
        resp = FakeResource2.delete_by_id(sess, r_id)
        self.assertIsNone(resp)
        headers = {'Accept': ''}
        sess.delete.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            endpoint_filter=FakeResource2.service,
            headers=headers)

        path_args = {"parent_name": "my_name"}
        resp = FakeResource2.delete_by_id(sess, r_id, path_args=path_args)
        self.assertIsNone(resp)
        headers = {'Accept': ''}
        sess.delete.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            endpoint_filter=FakeResource2.service,
            headers=headers)

    def test_create(self):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=fake_body)
        resp.headers = {'location': 'foo'}
        self.session.post = mock.Mock(return_value=resp)

        # Create resource with subset of attributes in order to
        # verify create refreshes all attributes from response.
        obj = FakeResource.new(parent_name=fake_parent,
                               name=fake_name,
                               enabled=True,
                               attr1=fake_attr1)

        self.assertEqual(obj, obj.create(self.session))
        self.assertFalse(obj.is_dirty)

        last_req = self.session.post.call_args[1]["json"][
            FakeResource.resource_key]

        self.assertEqual(4, len(last_req))
        self.assertTrue(last_req['enabled'])
        self.assertEqual(fake_parent, last_req['parent_name'])
        self.assertEqual(fake_name, last_req['name'])
        self.assertEqual(fake_attr1, last_req['attr1'])

        self.assertTrue(obj['enabled'])
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_parent, obj['parent_name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])
        self.assertIsNone(obj['status'])

        self.assertTrue(obj.enabled)
        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_parent, obj.parent_name)
        self.assertEqual(fake_parent, obj.parent)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr1, obj.attr1)
        self.assertEqual(fake_attr2, obj.second)
        self.assertEqual(fake_attr2, obj.attr2)
        self.assertIsNone(obj.status)
        self.assertEqual('foo', obj.location)

    def test_get(self):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=fake_body)
        resp.headers = {'location': 'foo'}
        self.session.get = mock.Mock(return_value=resp)

        # Create resource with subset of attributes in order to
        # verify get refreshes all attributes from response.
        obj = FakeResource.from_id(str(fake_id))
        obj['parent_name'] = fake_parent

        self.assertEqual(obj, obj.get(self.session))

        # Check that the proper URL is being built.
        self.assertCalledURL(self.session.get,
                             os.path.join(fake_base_path % fake_arguments,
                                          str(fake_id))[1:])

        self.assertTrue(obj['enabled'])
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_parent, obj['parent_name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])
        self.assertIsNone(obj['status'])

        self.assertTrue(obj.enabled)
        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_parent, obj.parent_name)
        self.assertEqual(fake_parent, obj.parent)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr1, obj.attr1)
        self.assertEqual(fake_attr2, obj.second)
        self.assertEqual(fake_attr2, obj.attr2)
        self.assertIsNone(obj.status)
        self.assertIsNone(obj.location)

    def test_get_by_id(self):
        resp = mock.Mock()
        resp.json = mock.Mock(return_value=fake_body)
        self.session.get = mock.Mock(return_value=resp)

        obj = FakeResource.get_by_id(self.session, fake_id,
                                     path_args=fake_arguments)

        # Check that the proper URL is being built.
        self.assertCalledURL(self.session.get,
                             os.path.join(fake_base_path % fake_arguments,
                                          str(fake_id))[1:])

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    def test_get_by_id_with_headers(self):
        header1 = "fake-value1"
        header2 = "fake-value2"
        headers = {"header1": header1,
                   "header2": header2}

        resp = mock.Mock(headers=headers)
        resp.json = mock.Mock(return_value=fake_body)
        self.session.get = mock.Mock(return_value=resp)

        class FakeResource2(FakeResource):
            header1 = resource.header("header1")
            header2 = resource.header("header2")

        obj = FakeResource2.get_by_id(self.session, fake_id,
                                      path_args=fake_arguments,
                                      include_headers=True)

        self.assertCalledURL(self.session.get,
                             os.path.join(fake_base_path % fake_arguments,
                                          str(fake_id))[1:])

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])
        self.assertEqual(header1, obj['headers']['header1'])
        self.assertEqual(header2, obj['headers']['header2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)
        self.assertEqual(header1, obj.header1)
        self.assertEqual(header2, obj.header2)

    def test_head_by_id(self):
        class FakeResource2(FakeResource):
            header1 = resource.header("header1")
            header2 = resource.header("header2")

        resp = mock.Mock(headers={"header1": "one", "header2": "two"})
        self.session.head = mock.Mock(return_value=resp)

        obj = FakeResource2.head_by_id(self.session, fake_id,
                                       path_args=fake_arguments)

        self.assertCalledURL(self.session.head,
                             os.path.join(fake_base_path % fake_arguments,
                                          str(fake_id))[1:])

        self.assertEqual('one', obj['headers']['header1'])
        self.assertEqual('two', obj['headers']['header2'])

        self.assertEqual('one', obj.header1)
        self.assertEqual('two', obj.header2)

    def test_patch_update(self):
        class FakeResourcePatch(FakeResource):
            patch_update = True

        resp = mock.Mock()
        resp.json = mock.Mock(return_value=fake_body)
        resp.headers = {'location': 'foo'}
        self.session.patch = mock.Mock(return_value=resp)

        # Create resource with subset of attributes in order to
        # verify update refreshes all attributes from response.
        obj = FakeResourcePatch.new(id=fake_id, parent_name=fake_parent,
                                    name=fake_name, attr1=fake_attr1)
        self.assertTrue(obj.is_dirty)

        self.assertEqual(obj, obj.update(self.session))
        self.assertFalse(obj.is_dirty)

        self.assertCalledURL(self.session.patch,
                             os.path.join(fake_base_path % fake_arguments,
                                          str(fake_id))[1:])

        last_req = self.session.patch.call_args[1]["json"][
            FakeResource.resource_key]

        self.assertEqual(3, len(last_req))
        self.assertEqual(fake_parent, last_req['parent_name'])
        self.assertEqual(fake_name, last_req['name'])
        self.assertEqual(fake_attr1, last_req['attr1'])

        self.assertTrue(obj['enabled'])
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_parent, obj['parent_name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])
        self.assertIsNone(obj['status'])

        self.assertTrue(obj.enabled)
        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_parent, obj.parent_name)
        self.assertEqual(fake_parent, obj.parent)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr1, obj.attr1)
        self.assertEqual(fake_attr2, obj.second)
        self.assertEqual(fake_attr2, obj.attr2)
        self.assertIsNone(obj.status)
        self.assertEqual('foo', obj.location)

    def test_put_update(self):
        class FakeResourcePut(FakeResource):
            # This is False by default, but explicit for this test.
            patch_update = False

        resp = mock.Mock()
        resp.json = mock.Mock(return_value=fake_body)
        resp.headers = {'location': 'foo'}
        self.session.put = mock.Mock(return_value=resp)

        # Create resource with subset of attributes in order to
        # verify update refreshes all attributes from response.
        obj = FakeResourcePut.new(id=fake_id, parent_name=fake_parent,
                                  name=fake_name, attr1=fake_attr1)
        self.assertTrue(obj.is_dirty)

        self.assertEqual(obj, obj.update(self.session))
        self.assertFalse(obj.is_dirty)

        self.assertCalledURL(self.session.put,
                             os.path.join(fake_base_path % fake_arguments,
                                          str(fake_id))[1:])

        last_req = self.session.put.call_args[1]["json"][
            FakeResource.resource_key]

        self.assertEqual(3, len(last_req))
        self.assertEqual(fake_parent, last_req['parent_name'])
        self.assertEqual(fake_name, last_req['name'])
        self.assertEqual(fake_attr1, last_req['attr1'])

        self.assertTrue(obj['enabled'])
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_parent, obj['parent_name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])
        self.assertIsNone(obj['status'])

        self.assertTrue(obj.enabled)
        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_parent, obj.parent_name)
        self.assertEqual(fake_parent, obj.parent)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr1, obj.attr1)
        self.assertEqual(fake_attr2, obj.second)
        self.assertEqual(fake_attr2, obj.attr2)
        self.assertIsNone(obj.status)
        self.assertEqual('foo', obj.location)

    def test_update_early_exit(self):
        obj = FakeResource()
        obj._dirty = []  # Bail out early if there's nothing to update.

        self.assertIsNone(obj.update("session"))

    def test_update_no_id_attribute(self):
        obj = FakeResource.existing(id=1, attr="value1",
                                    parent_name=fake_parent)
        obj.first = "value2"  # Make it dirty
        obj.update_by_id = mock.Mock(return_value=dict())
        # If no id_attribute is returned in the update response, make sure
        # we handle the resulting KeyError.
        self.assertEqual(obj, obj.update("session"))

    def test_delete(self):
        obj = FakeResource({"id": fake_id, "parent_name": fake_parent})
        obj.delete(self.session)

        self.assertCalledURL(self.session.delete,
                             os.path.join(fake_base_path % fake_arguments,
                                          str(fake_id))[1:])

    def _test_list(self, resource_class):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        for i in range(len(results)):
            results[i]['id'] = fake_id + i
        if resource_class.resources_key is not None:
            body = {resource_class.resources_key:
                    self._get_expected_results()}
            sentinel = {resource_class.resources_key: []}
        else:
            body = self._get_expected_results()
            sentinel = []
        resp1 = mock.Mock()
        resp1.json = mock.Mock(return_value=body)
        resp2 = mock.Mock()
        resp2.json = mock.Mock(return_value=sentinel)
        self.session.get.side_effect = [resp1, resp2]

        objs = list(resource_class.list(self.session, path_args=fake_arguments,
                                        paginated=True))

        params = {'limit': 3, 'marker': results[-1]['id']}
        self.assertEqual(params, self.session.get.call_args[1]['params'])
        self.assertEqual(3, len(objs))
        for obj in objs:
            self.assertIn(obj.id, range(fake_id, fake_id + 3))
            self.assertEqual(fake_name, obj['name'])
            self.assertEqual(fake_name, obj.name)
            self.assertIsInstance(obj, FakeResource)

    def _get_expected_results(self):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        for i in range(len(results)):
            results[i]['id'] = fake_id + i
        return results

    def test_list_keyed_resource(self):
        self._test_list(FakeResource)

    def test_list_non_keyed_resource(self):
        self._test_list(FakeResourceNoKeys)

    def _test_list_call_count(self, paginated):
        # Test that we've only made one call to receive all data
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        resp = mock.Mock()
        resp.json = mock.Mock(return_value={fake_resources: results})
        attrs = {"get.return_value": resp}
        session = mock.Mock(**attrs)

        list(FakeResource.list(session, params={'limit': len(results) + 1},
                               path_args=fake_arguments,
                               paginated=paginated))

        # Ensure we only made one call to complete this.
        self.assertEqual(1, session.get.call_count)

    def test_list_bail_out(self):
        # When we get less data than limit, make sure we made one call
        self._test_list_call_count(True)

    def test_list_nonpaginated(self):
        # When we call with paginated=False, make sure we made one call
        self._test_list_call_count(False)

    def test_determine_limit(self):
        full_page = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        last_page = [fake_data.copy()]

        session = mock.Mock()
        session.get = mock.Mock()
        full_response = mock.Mock()
        response_body = {FakeResource.resources_key: full_page}
        full_response.json = mock.Mock(return_value=response_body)
        last_response = mock.Mock()
        response_body = {FakeResource.resources_key: last_page}
        last_response.json = mock.Mock(return_value=response_body)
        pages = [full_response, full_response, last_response]
        session.get.side_effect = pages

        # Don't specify a limit. Resource.list will determine the limit
        # is 3 based on the first `full_page`.
        results = list(FakeResource.list(session, path_args=fake_arguments,
                       paginated=True))

        self.assertEqual(session.get.call_count, len(pages))
        self.assertEqual(len(full_page + full_page + last_page), len(results))

    def test_empty_list(self):
        page = []

        session = mock.Mock()
        session.get = mock.Mock()
        full_response = mock.Mock()
        response_body = {FakeResource.resources_key: page}
        full_response.json = mock.Mock(return_value=response_body)
        pages = [full_response]
        session.get.side_effect = pages

        results = list(FakeResource.list(session, path_args=fake_arguments,
                       paginated=True))

        self.assertEqual(session.get.call_count, len(pages))
        self.assertEqual(len(page), len(results))

    def test_attrs_name(self):
        obj = FakeResource()

        self.assertIsNone(obj.name)
        del obj.name

    def test_to_dict(self):
        kwargs = {
            'enabled': True,
            'name': 'FOO',
            'parent': 'dad',
            'attr1': 'BAR',
            'attr2': ['ZOO', 'BAZ'],
            'status': 'Active',
            'headers': {
                'key': 'value'
            }
        }
        obj = FakeResource(kwargs)
        res = obj.to_dict()
        self.assertIsInstance(res, dict)
        self.assertTrue(res['enabled'])
        self.assertEqual('FOO', res['name'])
        self.assertEqual('dad', res['parent'])
        self.assertEqual('BAR', res['attr1'])
        self.assertEqual(['ZOO', 'BAZ'], res['attr2'])
        self.assertEqual('Active', res['status'])
        self.assertNotIn('headers', res)

    def test_composite_attr_happy(self):
        obj = FakeResource.existing(**{'attr3': '3'})

        try:
            self.assertEqual('3', obj.third)
        except AttributeError:
            self.fail("third was not found as expected")

    def test_composite_attr_fallback(self):
        obj = FakeResource.existing(**{'attr_three': '3'})

        try:
            self.assertEqual('3', obj.third)
        except AttributeError:
            self.fail("third was not found in fallback as expected")

    def test_id_del(self):

        class Test(resource.Resource):
            id_attribute = "my_id"

        attrs = {"my_id": 100}
        t = Test(attrs=attrs)

        self.assertEqual(attrs["my_id"], t.id)
        del t.id
        self.assertTrue(Test.id_attribute not in t._attrs)

    def test_from_name_with_name(self):
        name = "Ernie Banks"

        obj = FakeResource.from_name(name)
        self.assertEqual(name, obj.name)

    def test_from_id_with_name(self):
        name = "Sandy Koufax"

        obj = FakeResource.from_id(name)
        self.assertEqual(name, obj.id)

    def test_from_id_with_object(self):
        name = "Mickey Mantle"
        obj = FakeResource.new(name=name)

        new_obj = FakeResource.from_id(obj)
        self.assertIs(new_obj, obj)
        self.assertEqual(obj.name, new_obj.name)

    def test_from_id_with_bad_value(self):
        def should_raise():
            FakeResource.from_id(3.14)

        self.assertThat(should_raise, matchers.raises(ValueError))

    def test_dirty_list(self):
        class Test(resource.Resource):
            attr = resource.prop("attr")

        # Check if dirty after setting by prop
        sot1 = Test()
        self.assertFalse(sot1.is_dirty)
        sot1.attr = 1
        self.assertTrue(sot1.is_dirty)

        # Check if dirty after setting by mapping
        sot2 = Test()
        sot2["attr"] = 1
        self.assertTrue(sot1.is_dirty)

        # Check if dirty after creation
        sot3 = Test({"attr": 1})
        self.assertTrue(sot3.is_dirty)

    def test_update_attrs(self):
        class Test(resource.Resource):
            moe = resource.prop("the-attr")
            larry = resource.prop("the-attr2")
            curly = resource.prop("the-attr3", type=int)
            shemp = resource.prop("the-attr4")

        value1 = "one"
        value2 = "two"
        value3 = "3"
        value4 = "fore"
        value5 = "fiver"

        sot = Test({"the-attr": value1})

        sot.update_attrs({"the-attr2": value2, "notprop": value4})
        self.assertTrue(sot.is_dirty)
        self.assertEqual(value1, sot.moe)
        self.assertEqual(value1, sot["the-attr"])
        self.assertEqual(value2, sot.larry)
        self.assertEqual(value4, sot.notprop)

        sot._reset_dirty()

        sot.update_attrs(curly=value3)
        self.assertTrue(sot.is_dirty)
        self.assertEqual(int, type(sot.curly))
        self.assertEqual(int(value3), sot.curly)

        sot._reset_dirty()

        sot.update_attrs(**{"the-attr4": value5})
        self.assertTrue(sot.is_dirty)
        self.assertEqual(value5, sot.shemp)

    def test_get_id(self):
        class Test(resource.Resource):
            pass

        ID = "an id"
        res = Test({"id": ID})

        self.assertEqual(ID, resource.Resource.get_id(ID))
        self.assertEqual(ID, resource.Resource.get_id(res))

    def test_convert_ids(self):
        class TestResourceFoo(resource.Resource):
            pass

        class TestResourceBar(resource.Resource):
            pass

        resfoo = TestResourceFoo({'id': 'FAKEFOO'})
        resbar = TestResourceBar({'id': 'FAKEBAR'})

        self.assertIsNone(resource.Resource.convert_ids(None))
        attrs = {
            'key1': 'value1'
        }
        self.assertEqual(attrs, resource.Resource.convert_ids(attrs))

        attrs = {
            'foo': resfoo,
            'bar': resbar,
            'other': 'whatever',
        }
        res = resource.Resource.convert_ids(attrs)
        self.assertEqual('FAKEFOO', res['foo'])
        self.assertEqual('FAKEBAR', res['bar'])
        self.assertEqual('whatever', res['other'])

    def test_repr(self):
        fr = FakeResource()
        fr._loaded = False
        fr.first = "hey"
        fr.second = "hi"
        fr.third = "nah"
        the_repr = repr(fr)
        the_repr = the_repr.replace('openstack.tests.unit.test_resource.', '')
        result = eval(the_repr)
        self.assertEqual(fr._loaded, result._loaded)
        self.assertEqual(fr.first, result.first)
        self.assertEqual(fr.second, result.second)
        self.assertEqual(fr.third, result.third)

    def test_id_attribute(self):
        faker = FakeResource(fake_data)
        self.assertEqual(fake_id, faker.id)
        faker.id_attribute = 'name'
        self.assertEqual(fake_name, faker.id)
        faker.id_attribute = 'attr1'
        self.assertEqual(fake_attr1, faker.id)
        faker.id_attribute = 'attr2'
        self.assertEqual(fake_attr2, faker.id)
        faker.id_attribute = 'id'
        self.assertEqual(fake_id, faker.id)

    def test_name_attribute(self):
        class Person_ES(resource.Resource):
            name_attribute = "nombre"
            nombre = resource.prop('nombre')

        name = "Brian"
        args = {'nombre': name}

        person = Person_ES(args)
        self.assertEqual(name, person.nombre)
        self.assertEqual(name, person.name)

        new_name = "Julien"
        person.name = new_name
        self.assertEqual(new_name, person.nombre)
        self.assertEqual(new_name, person.name)

    def test_boolstr_prop(self):
        faker = FakeResource(fake_data)
        self.assertTrue(faker.enabled)
        self.assertTrue(faker['enabled'])

        faker._attrs['enabled'] = False
        self.assertFalse(faker.enabled)
        self.assertFalse(faker['enabled'])

        # should fail fast
        def set_invalid():
            faker.enabled = 'INVALID'
        self.assertRaises(ValueError, set_invalid)


class ResourceMapping(base.TestCase):

    def test__getitem(self):
        value = 10

        class Test(resource.Resource):
            attr = resource.prop("attr")

        t = Test(attrs={"attr": value})

        self.assertEqual(value, t["attr"])

    def test__setitem__existing_item_changed(self):

        class Test(resource.Resource):
            pass

        t = Test()
        key = "attr"
        value = 1
        t[key] = value

        self.assertEqual(value, t._attrs[key])
        self.assertTrue(key in t._dirty)

    def test__setitem__existing_item_unchanged(self):

        class Test(resource.Resource):
            pass

        key = "attr"
        value = 1
        t = Test(attrs={key: value})
        t._reset_dirty()  # Clear dirty list so this checks as unchanged.
        t[key] = value

        self.assertEqual(value, t._attrs[key])
        self.assertTrue(key not in t._dirty)

    def test__setitem__new_item(self):

        class Test(resource.Resource):
            pass

        t = Test()
        key = "attr"
        value = 1
        t[key] = value

        self.assertEqual(value, t._attrs[key])
        self.assertTrue(key in t._dirty)

    def test__delitem__(self):

        class Test(resource.Resource):
            pass

        key = "attr"
        value = 1
        t = Test(attrs={key: value})

        del t[key]

        self.assertTrue(key not in t._attrs)
        self.assertTrue(key in t._dirty)

    def test__len__(self):

        class Test(resource.Resource):
            pass

        attrs = {"a": 1, "b": 2, "c": 3}
        t = Test(attrs=attrs)

        self.assertEqual(len(attrs.keys()), len(t))

    def test__iter__(self):

        class Test(resource.Resource):
            pass

        attrs = {"a": 1, "b": 2, "c": 3}
        t = Test(attrs=attrs)

        for attr in t:
            self.assertEqual(attrs[attr], t[attr])

    def _test_resource_serialization(self, session_method, resource_method):
        attr_type = resource.Resource

        class Test(resource.Resource):
            allow_create = True
            attr = resource.prop("attr", type=attr_type)

        the_id = 123
        sot = Test()
        sot.attr = resource.Resource({"id": the_id})
        self.assertEqual(attr_type, type(sot.attr))

        def fake_call(*args, **kwargs):
            attrs = kwargs["json"]
            try:
                json.dumps(attrs)
            except TypeError as e:
                self.fail("Unable to serialize _attrs: %s" % e)
            resp = mock.Mock()
            resp.json = mock.Mock(return_value=attrs)
            return resp

        session = mock.Mock()
        setattr(session, session_method, mock.Mock(side_effect=fake_call))

        if resource_method == "create_by_id":
            session.create_by_id(session, sot._attrs)
        elif resource_method == "update_by_id":
            session.update_by_id(session, None, sot._attrs)

    def test_create_serializes_resource_types(self):
        self._test_resource_serialization("post", "create_by_id")

    def test_update_serializes_resource_types(self):
        self._test_resource_serialization("patch", "update_by_id")


class FakeResponse(object):
    def __init__(self, response):
        self.body = response

    def json(self):
        return self.body


class TestFind(base.TestCase):
    NAME = 'matrix'
    ID = 'Fishburne'
    PROP = 'attribute2'

    def setUp(self):
        super(TestFind, self).setUp()
        self.mock_session = mock.Mock()
        self.mock_get = mock.Mock()
        self.mock_session.get = self.mock_get
        self.matrix = {'id': self.ID, 'name': self.NAME, 'prop': self.PROP}

    def test_name(self):
        self.mock_get.side_effect = [
            exceptions.NotFoundException(),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]

        result = FakeResource.find(self.mock_session, self.NAME,
                                   path_args=fake_arguments)

        self.assertEqual(self.NAME, result.name)
        self.assertEqual(self.PROP, result.prop)

    def test_id(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resource_key: self.matrix})
        ]

        result = FakeResource.find(self.mock_session, self.ID,
                                   path_args=fake_arguments)

        self.assertEqual(self.ID, result.id)
        self.assertEqual(self.PROP, result.prop)

        path = "fakes/" + fake_parent + "/data/" + self.ID
        self.mock_get.assert_any_call(path, endpoint_filter=None)

    def test_id_no_retrieve(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]

        class NoRetrieveResource(FakeResource):
            allow_retrieve = False

        result = NoRetrieveResource.find(self.mock_session, self.ID,
                                         path_args=fake_arguments)

        self.assertEqual(self.ID, result.id)
        self.assertEqual(self.PROP, result.prop)

    def test_dups(self):
        dupe = self.matrix.copy()
        dupe['id'] = 'different'
        self.mock_get.side_effect = [
            # Raise a 404 first so we get out of the ID search and into name.
            exceptions.NotFoundException(),
            FakeResponse({FakeResource.resources_key: [self.matrix, dupe]})
        ]

        self.assertRaises(exceptions.DuplicateResource, FakeResource.find,
                          self.mock_session, self.NAME)

    def test_id_attribute_find(self):
        floater = {'ip_address': "127.0.0.1", 'prop': self.PROP}
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resource_key: floater})
        ]

        FakeResource.id_attribute = 'ip_address'
        FakeResource.id_attribute = 'ip_address'
        result = FakeResource.find(self.mock_session, "127.0.0.1",
                                   path_args=fake_arguments)
        self.assertEqual("127.0.0.1", result.id)
        self.assertEqual(self.PROP, result.prop)

        FakeResource.id_attribute = 'id'

        p = {'ip_address': "127.0.0.1"}
        path = fake_path + "?limit=2"
        self.mock_get.called_once_with(path, params=p, endpoint_filter=None)

    def test_nada(self):
        self.mock_get.side_effect = [
            exceptions.NotFoundException(),
            FakeResponse({FakeResource.resources_key: []})
        ]

        self.assertIsNone(FakeResource.find(self.mock_session, self.NAME))

    def test_no_name(self):
        self.mock_get.side_effect = [
            exceptions.NotFoundException(),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]
        FakeResource.name_attribute = None

        self.assertIsNone(FakeResource.find(self.mock_session, self.NAME))

    def test_nada_not_ignored(self):
        self.mock_get.side_effect = [
            exceptions.NotFoundException(),
            FakeResponse({FakeResource.resources_key: []})
        ]

        self.assertRaises(exceptions.ResourceNotFound, FakeResource.find,
                          self.mock_session, self.NAME, ignore_missing=False)


class TestWaitForStatus(base.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestWaitForStatus, self).__init__(*args, **kwargs)
        self.build = FakeResponse(self.body_with_status(fake_body, 'BUILD'))
        self.active = FakeResponse(self.body_with_status(fake_body, 'ACTIVE'))
        self.error = FakeResponse(self.body_with_status(fake_body, 'ERROR'))

    def setUp(self):
        super(TestWaitForStatus, self).setUp()
        self.sess = mock.Mock()

    def body_with_status(self, body, status):
        body_copy = copy.deepcopy(body)
        body_copy[fake_resource]['status'] = status
        return body_copy

    def test_wait_for_status_nothing(self):
        self.sess.get = mock.Mock()
        sot = FakeResource.new(**fake_data)
        sot.status = 'ACTIVE'

        self.assertEqual(sot, resource.wait_for_status(
            self.sess, sot, 'ACTIVE', [], 1, 2))
        self.assertEqual([], self.sess.get.call_args_list)

    def test_wait_for_status(self):
        self.sess.get = mock.Mock()
        self.sess.get.side_effect = [self.build, self.active]
        sot = FakeResource.new(**fake_data)

        self.assertEqual(sot, resource.wait_for_status(
            self.sess, sot, 'ACTIVE', [], 1, 2))

    def test_wait_for_status_timeout(self):
        self.sess.get = mock.Mock()
        self.sess.get.side_effect = [self.build, self.build]
        sot = FakeResource.new(**fake_data)

        self.assertRaises(exceptions.ResourceTimeout, resource.wait_for_status,
                          self.sess, sot, 'ACTIVE', ['ERROR'], 1, 2)

    def test_wait_for_status_failures(self):
        self.sess.get = mock.Mock()
        self.sess.get.side_effect = [self.build, self.error]
        sot = FakeResource.new(**fake_data)

        self.assertRaises(exceptions.ResourceFailure, resource.wait_for_status,
                          self.sess, sot, 'ACTIVE', ['ERROR'], 1, 2)

    def test_wait_for_status_no_status(self):
        class FakeResourceNoStatus(resource.Resource):
            allow_retrieve = True

        sot = FakeResourceNoStatus.new(id=123)

        self.assertRaises(AttributeError, resource.wait_for_status,
                          self.sess, sot, 'ACTIVE', ['ERROR'], 1, 2)


class TestWaitForDelete(base.TestCase):

    def test_wait_for_delete(self):
        sess = mock.Mock()
        sot = FakeResource.new(**fake_data)
        sot.get = mock.Mock()
        sot.get.side_effect = [
            sot,
            exceptions.NotFoundException()]

        self.assertEqual(sot, resource.wait_for_delete(sess, sot, 1, 2))

    def test_wait_for_delete_fail(self):
        sess = mock.Mock()
        sot = FakeResource.new(**fake_data)
        sot.get = mock.Mock(return_value=sot)

        self.assertRaises(exceptions.ResourceTimeout, resource.wait_for_delete,
                          sess, sot, 1, 2)
