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


class PropTests(base.TestCase):

    def test_with_alias_and_type(self):
        class Test(resource.Resource):
            attr = resource.prop("attr1", alias="attr2", type=bool)

        t = Test(attrs={"attr2": 500})

        # Don't test with assertTrue because 500 evaluates to True.
        # Need to test that bool(500) happened and attr2 *is* True.
        self.assertIs(t.attr, True)

    def test_defaults(self):
        new_default = 100

        class Test(resource.Resource):
            attr1 = resource.prop("attr1")
            attr2 = resource.prop("attr2", default=new_default)

        t = Test()

        self.assertIsNone(t.attr1)
        self.assertEqual(t.attr2, new_default)

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
            header1 = resource.prop("header1")
            header2 = resource.prop("header2")

        obj = FakeResource2.get_by_id(self.session, fake_id,
                                      path_args=fake_arguments,
                                      include_headers=True)

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])
        self.assertEqual(header1, obj['header1'])
        self.assertEqual(header2, obj['header2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)
        self.assertEqual(header1, obj.header1)
        self.assertEqual(header2, obj.header2)

    @httpretty.activate
    def test_head(self):
        self.stub_url(httpretty.HEAD, path=[fake_path, fake_id],
                      name=fake_name,
                      attr1=fake_attr1,
                      attr2=fake_attr2)
        obj = FakeResource.head_by_id(self.session, fake_id,
                                      path_args=fake_arguments)

        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_update(self):
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
        self.assertEqual(1, len(last_req))
        self.assertEqual(fake_attr1, last_req['attr1'])

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

        put_data = {'id': fake_id, 'name': 'putty'}
        put_body = {fake_resource: put_data}
        self.stub_url(httpretty.PUT,
                      path=[fake_path, fake_id],
                      json=put_body)
        obj['attr1'] = 'update_again'
        FakeResource.put_update = True
        self.assertEqual(obj, obj.update(self.session))
        last_req = httpretty.last_request()
        self.assertEqual('PUT', last_req.command)
        last_data = last_req.parsed_body[fake_resource]
        self.assertEqual(1, len(last_data))
        self.assertEqual('update_again', last_data['attr1'])

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
    def test_list(self):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        for i in range(len(results)):
            results[i]['id'] = fake_id + i

        marker = "marker=%d" % results[-1]['id']
        self.stub_url(httpretty.GET,
                      path=[fake_path + "?" + marker],
                      json={fake_resources: []},
                      match_querystring=True)
        self.stub_url(httpretty.GET,
                      path=[fake_path],
                      json={fake_resources: results})

        objs = FakeResource.list(self.session, limit=1,
                                 path_args=fake_arguments)
        objs = list(objs)
        self.assertIn(marker, httpretty.last_request().path)
        self.assertEqual(3, len(objs))

        for obj in objs:
            self.assertIn(obj.id, range(fake_id, fake_id + 3))
            self.assertEqual(fake_name, obj['name'])
            self.assertEqual(fake_name, obj.name)
            self.assertIsInstance(obj, FakeResource)

    def test_list_bail_out(self):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        body = mock.Mock(body={fake_resources: results})
        attrs = {"get.return_value": body}
        session = mock.Mock(**attrs)

        list(FakeResource.list(session, limit=len(results) + 1,
                               path_args=fake_arguments))

        # Ensure we only made one call to complete this.
        self.assertEqual(session.get.call_count, 1)

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

        objs = FakeResource.page(session, None, None)

        self.assertEqual(records, objs)
        path = fake_base_path
        session.get.assert_called_with(path, params={}, service=None)

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

    def test_repr_name(self):
        FakeResource.resource_name = 'foo'
        self.assertEqual('foo: {}', repr(FakeResource()))
        FakeResource.resource_name = None
        FakeResource.resource_key = None
        self.assertEqual('FakeResource: {}', repr(FakeResource()))
        FakeResource.resource_key = fake_resource
        self.assertEqual(fake_resource + ': {}', repr(FakeResource()))

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
