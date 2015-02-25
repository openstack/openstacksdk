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

import httpretty
import mock
from testtools import matchers

from openstack import exceptions
from openstack import format
from openstack import resource
from openstack import session
from openstack.tests import base
from openstack.tests import fakes
from openstack import transport
from openstack import utils

fake_name = 'rey'
fake_id = 99
fake_attr1 = 'lana'
fake_attr2 = 'del'

fake_resource = 'fake'
fake_resources = 'fakes'
fake_arguments = {'name': 'rey'}
fake_base_path = '/fakes/%(name)s/data'
fake_path = '/fakes/rey/data'

fake_data = {'id': fake_id,
             'enabled': True,
             'name': fake_name,
             'attr1': fake_attr1,
             'attr2': fake_attr2}
fake_body = {fake_resource: fake_data}


class FakeResource(resource.Resource):

    resource_key = fake_resource
    resources_key = fake_resources
    base_path = fake_base_path

    allow_create = allow_retrieve = allow_update = True
    allow_delete = allow_list = allow_head = True

    enabled = resource.prop('enabled', type=format.BoolStr)
    name = resource.prop('name')
    first = resource.prop('attr1')
    second = resource.prop('attr2')
    third = resource.prop('attr3', alias='attr_three')


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
        self.assertEqual(t.attr2, new_default)

        # When the default value is passed in, it is left untouched.
        # Check that attr2 is literally the same object we set as default.
        t.attr2 = new_default
        self.assertIs(t.attr2, new_default)

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
        self.assertEqual(sot.shortstop, resource1)
        self.assertEqual(sot.shortstop.id, id1)
        self.assertEqual(type(sot.shortstop), FakeResource)

        resource2 = FakeResource.new(id=id2)
        self.assertEqual(sot.third_base, resource2)
        self.assertEqual(sot.third_base.id, id2)
        self.assertEqual(type(sot.third_base), FakeResource)

        sot2 = FakestResource()
        sot2.shortstop = resource1
        sot2.third_base = resource2
        self.assertEqual(sot2.shortstop, resource1)
        self.assertEqual(sot2.shortstop.id, id1)
        self.assertEqual(type(sot2.shortstop), FakeResource)
        self.assertEqual(sot2.third_base, resource2)
        self.assertEqual(sot2.third_base.id, id2)
        self.assertEqual(type(sot2.third_base), FakeResource)

        body = {
            "shortstop": id1,
            "third_base": id2
        }
        sot3 = FakestResource(body)
        self.assertEqual(sot3.shortstop, FakeResource({"id": id1}))
        self.assertEqual(sot3.third_base, FakeResource({"id": id2}))

    def test_set_alias_same_name(self):
        class Test(resource.Resource):
            attr = resource.prop("something", alias="attr")

        val = "hey"
        args = {"attr": val}
        sot = Test(args)

        self.assertEqual(sot._attrs["something"], val)
        self.assertIsNone(sot._attrs.get("attr"))
        self.assertEqual(sot.attr, val)


class HeaderTests(base.TestCase):
    class Test(resource.Resource):
        hey = resource.header("vocals")
        ho = resource.header("guitar")
        letsgo = resource.header("bass")

    def test_get(self):
        val = "joey"
        args = {"vocals": val}
        sot = HeaderTests.Test({'headers': args})
        self.assertEqual(val, sot.hey)
        self.assertEqual(None, sot.ho)
        self.assertEqual(None, sot.letsgo)

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


class ResourceTests(base.TestTransportBase):

    TEST_URL = fakes.FakeAuthenticator.ENDPOINT

    def setUp(self):
        super(ResourceTests, self).setUp()
        self.transport = transport.Transport(accept=transport.JSON)
        self.auth = fakes.FakeAuthenticator()
        self.session = session.Session(self.transport, self.auth)

    @httpretty.activate
    def test_empty_id(self):
        self.stub_url(httpretty.GET, path=[fake_path], json=fake_body)
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
                           attrs, json_body):

        class FakeResource2(FakeResource):
            resource_key = key
            service = "my_service"

        response = mock.MagicMock()
        response.body = response_body

        sess = mock.MagicMock()
        sess.put = mock.MagicMock(return_value=response)
        sess.post = mock.MagicMock(return_value=response)

        resp = FakeResource2.create_by_id(sess, attrs)
        self.assertEqual(resp, response_value)
        sess.post.assert_called_with(FakeResource2.base_path,
                                     service=FakeResource2.service,
                                     json=json_body)

        r_id = "my_id"
        resp = FakeResource2.create_by_id(sess, attrs, resource_id=r_id)
        self.assertEqual(resp, response_value)
        sess.put.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            service=FakeResource2.service,
            json=json_body)

        path_args = {"name": "my_name"}
        resp = FakeResource2.create_by_id(sess, attrs, path_args=path_args)
        self.assertEqual(resp, response_value)
        sess.post.assert_called_with(FakeResource2.base_path % path_args,
                                     service=FakeResource2.service,
                                     json=json_body)

        resp = FakeResource2.create_by_id(sess, attrs, resource_id=r_id,
                                          path_args=path_args)
        self.assertEqual(resp, response_value)
        sess.put.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            service=FakeResource2.service,
            json=json_body)

    def test_create_without_resource_key(self):
        key = None
        response_value = [1, 2, 3]
        response_body = response_value
        attrs = {"a": 1, "b": 2, "c": 3}
        json_body = attrs
        self._test_create_by_id(key, response_value, response_body,
                                attrs, json_body)

    def test_create_with_resource_key(self):
        key = "my_key"
        response_value = [1, 2, 3]
        response_body = {key: response_value}
        attrs = {"a": 1, "b": 2, "c": 3}
        json_body = {key: attrs}
        self._test_create_by_id(key, response_value, response_body,
                                attrs, json_body)

    def _test_get_data_by_id(self, key, response_value, response_body):
        class FakeResource2(FakeResource):
            resource_key = key
            service = "my_service"

        response = mock.MagicMock()
        response.body = response_body

        sess = mock.MagicMock()
        sess.get = mock.MagicMock(return_value=response)

        r_id = "my_id"
        resp = FakeResource2.get_data_by_id(sess, resource_id=r_id)
        self.assertEqual(resp, response_value)
        sess.get.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            service=FakeResource2.service)

        path_args = {"name": "my_name"}
        resp = FakeResource2.get_data_by_id(sess, resource_id=r_id,
                                            path_args=path_args)
        self.assertEqual(resp, response_value)
        sess.get.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            service=FakeResource2.service)

    def test_get_data_without_resource_key(self):
        key = None
        response_value = [1, 2, 3]
        response_body = response_value
        self._test_get_data_by_id(key, response_value, response_body)

    def test_get_data_with_resource_key(self):
        key = "my_key"
        response_value = [1, 2, 3]
        response_body = {key: response_value}
        self._test_get_data_by_id(key, response_value, response_body)

    def _test_head_data_by_id(self, key, response_value):
        class FakeResource2(FakeResource):
            resource_key = key
            service = "my_service"

        response = mock.MagicMock()
        response.headers = response_value

        sess = mock.MagicMock()
        sess.head = mock.MagicMock(return_value=response)

        r_id = "my_id"
        resp = FakeResource2.head_data_by_id(sess, resource_id=r_id)
        self.assertEqual({'headers': response_value}, resp)
        sess.head.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            service=FakeResource2.service,
            accept=None)

        path_args = {"name": "my_name"}
        resp = FakeResource2.head_data_by_id(sess, resource_id=r_id,
                                             path_args=path_args)
        self.assertEqual({'headers': response_value}, resp)
        sess.head.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            service=FakeResource2.service,
            accept=None)

    def test_head_data_without_resource_key(self):
        key = None
        response_value = {"key1": "value1", "key2": "value2"}
        self._test_head_data_by_id(key, response_value)

    def test_head_data_with_resource_key(self):
        key = "my_key"
        response_value = {"key1": "value1", "key2": "value2"}
        self._test_head_data_by_id(key, response_value)

    def _test_update_by_id(self, key, response_value, response_body,
                           attrs, json_body):

        class FakeResource2(FakeResource):
            resource_key = key
            service = "my_service"

        response = mock.MagicMock()
        response.body = response_body

        sess = mock.MagicMock()
        sess.patch = mock.MagicMock(return_value=response)

        r_id = "my_id"
        resp = FakeResource2.update_by_id(sess, r_id, attrs)
        self.assertEqual(resp, response_value)
        sess.patch.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            service=FakeResource2.service,
            json=json_body)

        path_args = {"name": "my_name"}
        resp = FakeResource2.update_by_id(sess, r_id, attrs,
                                          path_args=path_args)
        self.assertEqual(resp, response_value)
        sess.patch.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            service=FakeResource2.service,
            json=json_body)

    def test_update_without_resource_key(self):
        key = None
        response_value = [1, 2, 3]
        response_body = response_value
        attrs = {"a": 1, "b": 2, "c": 3}
        json_body = attrs
        self._test_update_by_id(key, response_value, response_body,
                                attrs, json_body)

    def test_update_with_resource_key(self):
        key = "my_key"
        response_value = [1, 2, 3]
        response_body = {key: response_value}
        attrs = {"a": 1, "b": 2, "c": 3}
        json_body = {key: attrs}
        self._test_update_by_id(key, response_value, response_body,
                                attrs, json_body)

    def test_delete_by_id(self):
        class FakeResource2(FakeResource):
            service = "my_service"

        sess = mock.MagicMock()
        sess.delete = mock.MagicMock(return_value=None)

        r_id = "my_id"
        resp = FakeResource2.delete_by_id(sess, r_id)
        self.assertIsNone(resp)
        sess.delete.assert_called_with(
            utils.urljoin(FakeResource2.base_path, r_id),
            service=FakeResource2.service,
            accept=None)

        path_args = {"name": "my_name"}
        resp = FakeResource2.delete_by_id(sess, r_id, path_args=path_args)
        self.assertIsNone(resp)
        sess.delete.assert_called_with(
            utils.urljoin(FakeResource2.base_path % path_args, r_id),
            service=FakeResource2.service,
            accept=None)

    @httpretty.activate
    def test_create(self):
        self.stub_url(httpretty.POST, path=fake_path, json=fake_body)

        obj = FakeResource.new(name=fake_name,
                               enabled=True,
                               attr1=fake_attr1,
                               attr2=fake_attr2)

        self.assertEqual(obj, obj.create(self.session))
        self.assertFalse(obj.is_dirty)

        last_req = httpretty.last_request().parsed_body[fake_resource]

        self.assertEqual(4, len(last_req))
        self.assertEqual('True', last_req['enabled'])
        self.assertEqual(fake_name, last_req['name'])
        self.assertEqual(fake_attr1, last_req['attr1'])
        self.assertEqual(fake_attr2, last_req['attr2'])

        self.assertEqual(fake_id, obj.id)
        self.assertEqual('True', obj['enabled'])
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(True, obj.enabled)
        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_get(self):
        self.stub_url(httpretty.GET, path=[fake_path, fake_id], json=fake_body)
        obj = FakeResource.get_by_id(self.session, fake_id,
                                     path_args=fake_arguments)

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_get_with_headers(self):
        header1 = "fake-value1"
        header2 = "fake-value2"
        headers = {"header1": header1,
                   "header2": header2}
        self.stub_url(httpretty.GET, path=[fake_path, fake_id], json=fake_body,
                      **headers)

        class FakeResource2(FakeResource):
            header1 = resource.header("header1")
            header2 = resource.header("header2")

        obj = FakeResource2.get_by_id(self.session, fake_id,
                                      path_args=fake_arguments,
                                      include_headers=True)

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

    @httpretty.activate
    def test_head(self):
        class FakeResource2(FakeResource):
            header1 = resource.header("header1")
            header2 = resource.header("header2")

        self.stub_url(httpretty.HEAD, path=[fake_path, fake_id],
                      header1='one',
                      header2='two')
        obj = FakeResource2.head_by_id(self.session, fake_id,
                                       path_args=fake_arguments)

        self.assertEqual('one', obj['headers']['header1'])
        self.assertEqual('two', obj['headers']['header2'])

        self.assertEqual('one', obj.header1)
        self.assertEqual('two', obj.header2)

    @httpretty.activate
    def test_update(self):
        FakeResource.put_update = False
        new_attr1 = 'attr5'
        new_attr2 = 'attr6'
        fake_body1 = copy.deepcopy(fake_body)
        fake_body1[fake_resource]['attr1'] = new_attr1

        self.stub_url(httpretty.POST, path=fake_path, json=fake_body1)
        self.stub_url(httpretty.PATCH,
                      path=[fake_path, fake_id],
                      json=fake_body)

        obj = FakeResource.new(name=fake_name,
                               attr1=new_attr1,
                               attr2=new_attr2)
        self.assertEqual(obj, obj.create(self.session))
        self.assertFalse(obj.is_dirty)
        self.assertEqual(new_attr1, obj['attr1'])

        obj['attr1'] = fake_attr1
        obj.second = fake_attr2
        self.assertTrue(obj.is_dirty)

        self.assertEqual(obj, obj.update(self.session))
        self.assertFalse(obj.is_dirty)

        last_req = httpretty.last_request().parsed_body[fake_resource]
        self.assertEqual(2, len(last_req))
        self.assertEqual(fake_attr1, last_req['attr1'])

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

        obj = FakeResource.new(id=fake_id,
                               name=fake_name,
                               attr1=new_attr1,
                               attr2=new_attr2)
        put_data = {'id': fake_id}
        put_body = {fake_resource: put_data}
        self.stub_url(httpretty.PUT,
                      path=[fake_path, fake_id],
                      json=put_body)
        FakeResource.put_update = True
        self.assertEqual(obj, obj.update(self.session))
        FakeResource.put_update = False
        last_req = httpretty.last_request()
        self.assertEqual('PUT', last_req.command)
        last_data = last_req.parsed_body[fake_resource]
        self.assertEqual(3, len(last_data))
        self.assertEqual(new_attr2, last_data['attr2'])
        self.assertEqual(new_attr1, last_data['attr1'])
        self.assertEqual(fake_name, last_data['name'])

    def test_update_early_exit(self):
        obj = FakeResource()
        obj._dirty = []  # Bail out early if there's nothing to update.

        self.assertIsNone(obj.update("session"))

    def test_update_no_id_attribute(self):
        obj = FakeResource.new(id=1, attr="value1")
        obj._dirty = {"attr": "value2"}
        obj.update_by_id = mock.MagicMock(return_value=dict())
        # If no id_attribute is returned in the update response, make sure
        # we handle the resulting KeyError.
        self.assertEqual(obj.update("session"), obj)

    @httpretty.activate
    def test_delete(self):
        self.stub_url(httpretty.GET, path=[fake_path, fake_id], json=fake_body)
        self.stub_url(httpretty.DELETE, [fake_path, fake_id])
        obj = FakeResource.get_by_id(self.session, fake_id,
                                     path_args=fake_arguments)

        obj.delete(self.session)

        last_req = httpretty.last_request()
        self.assertEqual('DELETE', last_req.method)
        self.assertEqual('/endpoint/fakes/rey/data/99', last_req.path)

    @httpretty.activate
    def _test_list(self, json_sentinel, json_body, resource_class):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        for i in range(len(results)):
            results[i]['id'] = fake_id + i

        marker = "marker=%d" % results[-1]['id']
        self.stub_url(httpretty.GET,
                      path=[fake_path + "?" + marker],
                      json=json_sentinel,
                      match_querystring=True)
        self.stub_url(httpretty.GET,
                      path=[fake_path],
                      json=json_body)

        objs = resource_class.list(self.session, limit=1,
                                   path_args=fake_arguments,
                                   paginated=True)
        objs = list(objs)
        self.assertIn(marker, httpretty.last_request().path)
        self.assertEqual(3, len(objs))

        for obj in objs:
            self.assertIn(obj.id, range(fake_id, fake_id + 3))
            self.assertEqual(fake_name, obj['name'])
            self.assertEqual(fake_name, obj.name)
            self.assertIsInstance(obj, FakeResource)

    def _test_list_call_count(self, paginated):
        # Test that we've only made one call to receive all data
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        body = mock.Mock(body={fake_resources: results})
        attrs = {"get.return_value": body}
        session = mock.Mock(**attrs)

        list(FakeResource.list(session, limit=len(results) + 1,
                               path_args=fake_arguments,
                               paginated=paginated))

        # Ensure we only made one call to complete this.
        self.assertEqual(session.get.call_count, 1)

    def test_list_bail_out(self):
        # When we get less data than limit, make sure we made one call
        self._test_list_call_count(True)

    def test_list_nonpaginated(self):
        # When we call with paginated=False, make sure we made one call
        self._test_list_call_count(False)

    def test_page(self):
        session = mock.Mock()
        session.get = mock.Mock()
        records = [{'id': 'squid'}]
        response = FakeResponse({FakeResource.resources_key: records})
        session.get.return_value = response

        objs = FakeResource.page(session, 1, None, path_args=fake_arguments)

        self.assertEqual(records, objs)
        path = fake_path + '?limit=1'
        session.get.assert_called_with(path, params={}, service=None)

        objs = FakeResource.page(session, None, 'a', path_args=fake_arguments)

        self.assertEqual(records, objs)
        path = fake_path + '?marker=a'
        session.get.assert_called_with(path, params={}, service=None)

        objs = FakeResource.page(session, None, None, path_args=fake_arguments)

        self.assertEqual(records, objs)
        path = fake_path
        session.get.assert_called_with(path, params={}, service=None)

        objs = FakeResource.page(session)

        self.assertEqual(records, objs)
        path = fake_base_path
        session.get.assert_called_with(path, params={}, service=None)

    def _get_expected_results(self):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        for i in range(len(results)):
            results[i]['id'] = fake_id + i
        return results

    @httpretty.activate
    def test_list_keyed_resource(self):
        sentinel = {fake_resources: []}
        body = {fake_resources: self._get_expected_results()}
        cls = FakeResource
        self._test_list(sentinel, body, cls)

    @httpretty.activate
    def test_list_non_keyed_resource(self):
        sentinel = []
        body = self._get_expected_results()
        cls = FakeResourceNoKeys
        self._test_list(sentinel, body, cls)

    def test_attrs(self):
        obj = FakeResource()

        self.assertIsNone(obj.name)
        del obj.name

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

        self.assertEqual(t.id, attrs["my_id"])
        del t.id
        self.assertTrue(Test.id_attribute not in t._attrs)

    def test_from_name_with_name(self):
        name = "Ernie Banks"

        obj = FakeResource.from_name(name)
        self.assertEqual(obj.name, name)

    def test_from_id_with_name(self):
        name = "Sandy Koufax"

        obj = FakeResource.from_id(name)
        self.assertEqual(obj.id, name)

    def test_from_id_with_object(self):
        name = "Mickey Mantle"
        obj = FakeResource.new(name=name)

        new_obj = FakeResource.from_id(obj)
        self.assertIs(new_obj, obj)
        self.assertEqual(new_obj.name, obj.name)

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

        value1 = "one"
        value2 = "two"
        value3 = "3"
        value4 = "fore"

        sot = Test({"the-attr": value1})

        sot.update_attrs({"the-attr2": value2, "notprop": value4})
        sot.update_attrs(curly=value3)

        self.assertEqual(value1, sot.moe)
        self.assertEqual(value1, sot["the-attr"])
        self.assertEqual(value2, sot.larry)
        self.assertEqual(int, type(sot.curly))
        self.assertEqual(int(value3), sot.curly)
        self.assertEqual(value4, sot["notprop"])


class ResourceMapping(base.TestCase):

    def test__getitem(self):
        value = 10

        class Test(resource.Resource):
            attr = resource.prop("attr")

        t = Test(attrs={"attr": value})

        self.assertEqual(t["attr"], value)

    def test__setitem__existing_item_changed(self):

        class Test(resource.Resource):
            pass

        t = Test()
        key = "attr"
        value = 1
        t[key] = value

        self.assertEqual(t._attrs[key], value)
        self.assertTrue(key in t._dirty)

    def test__setitem__existing_item_unchanged(self):

        class Test(resource.Resource):
            pass

        key = "attr"
        value = 1
        t = Test(attrs={key: value})
        t._reset_dirty()  # Clear dirty list so this checks as unchanged.
        t[key] = value

        self.assertEqual(t._attrs[key], value)
        self.assertTrue(key not in t._dirty)

    def test__setitem__new_item(self):

        class Test(resource.Resource):
            pass

        t = Test()
        key = "attr"
        value = 1
        t[key] = value

        self.assertEqual(t._attrs[key], value)
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

        self.assertEqual(len(t), len(attrs.keys()))

    def test__iter__(self):

        class Test(resource.Resource):
            pass

        attrs = {"a": 1, "b": 2, "c": 3}
        t = Test(attrs=attrs)

        for attr in t:
            self.assertEqual(t[attr], attrs[attr])

    def _test_resource_serialization(self, session_method, resource_method):
        attr_type = resource.Resource

        class Test(resource.Resource):
            allow_create = True
            attr = resource.prop("attr", type=attr_type)

        the_id = 123
        sot = Test()
        sot.attr = resource.Resource({"id": the_id})
        self.assertEqual(type(sot.attr), attr_type)

        def fake_call(*args, **kwargs):
            attrs = kwargs["json"]
            try:
                json.dumps(attrs)
            except TypeError as e:
                self.fail("Unable to serialize _attrs: %s" % e)
            return mock.Mock(body=attrs)

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


class FakeResponse:
    def __init__(self, response):
        self.body = response


class TestFind(base.TestCase):
    NAME = 'matrix'
    ID = 'Fishburne'

    def setUp(self):
        super(TestFind, self).setUp()
        self.mock_session = mock.Mock()
        self.mock_get = mock.Mock()
        self.mock_session.get = self.mock_get
        self.matrix = {'id': self.ID}

    def test_name(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: []}),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]

        result = FakeResource.find(self.mock_session, self.NAME,
                                   path_args=fake_arguments)

        self.assertEqual(self.ID, result.id)
        p = {'fields': 'id', 'name': self.NAME}
        path = fake_path + "?limit=2"
        self.mock_get.assert_any_call(path, params=p, service=None)

    def test_id(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]

        result = FakeResource.find(self.mock_session, self.ID,
                                   path_args=fake_arguments)

        self.assertEqual(self.ID, result.id)
        p = {'fields': 'id', 'id': self.ID}
        path = fake_path + "?limit=2"
        self.mock_get.assert_any_call(path, params=p, service=None)

    def test_nameo(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: []}),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]
        FakeResource.name_attribute = 'nameo'

        result = FakeResource.find(self.mock_session, self.NAME,
                                   path_args=fake_arguments)

        FakeResource.name_attribute = 'name'
        self.assertEqual(self.ID, result.id)
        p = {'fields': 'id', 'nameo': self.NAME}
        path = fake_path + "?limit=2"
        self.mock_get.assert_any_call(path, params=p, service=None)

    def test_dups(self):
        dup = {'id': 'Larry'}
        resp = FakeResponse({FakeResource.resources_key: [self.matrix, dup]})
        self.mock_get.return_value = resp

        self.assertRaises(exceptions.DuplicateResource, FakeResource.find,
                          self.mock_session, self.NAME)

    def test_id_attribute_find(self):
        floater = {'ip_address': "127.0.0.1"}
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: [floater]})
        ]

        FakeResource.id_attribute = 'ip_address'
        result = FakeResource.find(self.mock_session, "127.0.0.1",
                                   path_args=fake_arguments)
        self.assertEqual("127.0.0.1", result.id)
        FakeResource.id_attribute = 'id'

        p = {'fields': 'ip_address', 'ip_address': "127.0.0.1"}
        path = fake_path + "?limit=2"
        self.mock_get.assert_any_call(path, params=p, service=None)

    def test_nada(self):
        resp = FakeResponse({FakeResource.resources_key: []})
        self.mock_get.return_value = resp

        self.assertEqual(None, FakeResource.find(self.mock_session, self.NAME))

    def test_no_name(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: []}),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]
        FakeResource.name_attribute = None

        self.assertEqual(None, FakeResource.find(self.mock_session, self.NAME))

    def test_repr(self):
        fr = FakeResource()
        fr._loaded = False
        fr.first = "hey"
        fr.second = "hi"
        fr.third = "nah"
        the_repr = repr(fr)
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
        self.assertEqual(person.nombre, name)
        self.assertEqual(person.name, name)

        new_name = "Julien"
        person.name = new_name
        self.assertEqual(person.nombre, new_name)
        self.assertEqual(person.name, new_name)

    def test_boolstr_prop(self):
        faker = FakeResource(fake_data)
        self.assertEqual(True, faker.enabled)
        self.assertEqual('True', faker['enabled'])

        faker.enabled = False
        self.assertEqual(False, faker.enabled)
        self.assertEqual('False', faker['enabled'])

        # should fail fast
        def set_invalid():
            faker.enabled = 'INVALID'
        self.assertRaises(ValueError, set_invalid)

    @mock.patch("openstack.resource.Resource.list")
    def test_fallthrough(self, mock_list):
        class FakeResource2(FakeResource):
            name_attribute = None

            @classmethod
            def page(cls, session, limit=None, marker=None, path_args=None,
                     **params):
                raise exceptions.HttpException("exception")

        self.assertEqual(None, FakeResource2.find("session", "123"))
