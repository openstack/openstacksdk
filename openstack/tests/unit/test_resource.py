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

import itertools

from keystoneauth1 import adapter
import mock
import requests
import six

from openstack import exceptions
from openstack import format
from openstack import resource
from openstack.tests.unit import base


class FakeResponse(object):
    def __init__(self, response, status_code=200, headers=None):
        self.body = response
        self.status_code = status_code
        headers = headers if headers else {'content-type': 'application/json'}
        self.headers = requests.structures.CaseInsensitiveDict(headers)

    def json(self):
        return self.body


class TestComponent(base.TestCase):

    class ExampleComponent(resource._BaseComponent):
        key = "_example"

    # Since we're testing ExampleComponent, which is as isolated as we
    # can test _BaseComponent due to it's needing to be a data member
    # of a class that has an attribute on the parent class named `key`,
    # each test has to implement a class with a name that is the same
    # as ExampleComponent.key, which should be a dict containing the
    # keys and values to test against.

    def test_implementations(self):
        self.assertEqual("_body", resource.Body.key)
        self.assertEqual("_header", resource.Header.key)
        self.assertEqual("_uri", resource.URI.key)

    def test_creation(self):
        sot = resource._BaseComponent(
            "name", type=int, default=1, alternate_id=True)

        self.assertEqual("name", sot.name)
        self.assertEqual(int, sot.type)
        self.assertEqual(1, sot.default)
        self.assertTrue(sot.alternate_id)

    def test_get_no_instance(self):
        sot = resource._BaseComponent("test")

        # Test that we short-circuit everything when given no instance.
        result = sot.__get__(None, None)
        self.assertIsNone(result)

    # NOTE: Some tests will use a default=1 setting when testing result
    # values that should be None because the default-for-default is also None.
    def test_get_name_None(self):
        name = "name"

        class Parent(object):
            _example = {name: None}

        instance = Parent()
        sot = TestComponent.ExampleComponent(name, default=1)

        # Test that we short-circuit any typing of a None value.
        result = sot.__get__(instance, None)
        self.assertIsNone(result)

    def test_get_default(self):
        expected_result = 123

        class Parent(object):
            _example = {}

        instance = Parent()
        # NOTE: type=dict but the default value is an int. If we didn't
        # short-circuit the typing part of __get__ it would fail.
        sot = TestComponent.ExampleComponent("name", type=dict,
                                             default=expected_result)

        # Test that we directly return any default value.
        result = sot.__get__(instance, None)
        self.assertEqual(expected_result, result)

    def test_get_name_untyped(self):
        name = "name"
        expected_result = 123

        class Parent(object):
            _example = {name: expected_result}

        instance = Parent()
        sot = TestComponent.ExampleComponent("name")

        # Test that we return any the value as it is set.
        result = sot.__get__(instance, None)
        self.assertEqual(expected_result, result)

    # The code path for typing after a raw value has been found is the same.
    def test_get_name_typed(self):
        name = "name"
        value = "123"

        class Parent(object):
            _example = {name: value}

        instance = Parent()
        sot = TestComponent.ExampleComponent("name", type=int)

        # Test that we run the underlying value through type conversion.
        result = sot.__get__(instance, None)
        self.assertEqual(int(value), result)

    def test_get_name_formatter(self):
        name = "name"
        value = "123"
        expected_result = "one hundred twenty three"

        class Parent(object):
            _example = {name: value}

        class FakeFormatter(format.Formatter):
            @classmethod
            def deserialize(cls, value):
                return expected_result

        instance = Parent()
        sot = TestComponent.ExampleComponent("name", type=FakeFormatter)

        # Mock out issubclass rather than having an actual format.Formatter
        # This can't be mocked via decorator, isolate it to wrapping the call.
        result = sot.__get__(instance, None)
        self.assertEqual(expected_result, result)

    def test_set_name_untyped(self):
        name = "name"
        expected_value = "123"

        class Parent(object):
            _example = {}

        instance = Parent()
        sot = TestComponent.ExampleComponent("name")

        # Test that we don't run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual(expected_value, instance._example[name])

    def test_set_name_typed(self):
        expected_value = "123"

        class Parent(object):
            _example = {}

        instance = Parent()

        # The type we give to ExampleComponent has to be an actual type,
        # not an instance, so we can't get the niceties of a mock.Mock
        # instance that would allow us to call `assert_called_once_with` to
        # ensure that we're sending the value through the type.
        # Instead, we use this tiny version of a similar thing.
        class FakeType(object):
            calls = []

            def __init__(self, arg):
                FakeType.calls.append(arg)

        sot = TestComponent.ExampleComponent("name", type=FakeType)

        # Test that we run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual([expected_value], FakeType.calls)

    def test_set_name_formatter(self):
        expected_value = "123"

        class Parent(object):
            _example = {}

        instance = Parent()

        # As with test_set_name_typed, create a pseudo-Mock to track what
        # gets called on the type.
        class FakeFormatter(format.Formatter):
            calls = []

            @classmethod
            def serialize(cls, arg):
                FakeFormatter.calls.append(arg)

            @classmethod
            def deserialize(cls, arg):
                FakeFormatter.calls.append(arg)

        sot = TestComponent.ExampleComponent("name", type=FakeFormatter)

        # Test that we run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual([expected_value], FakeFormatter.calls)

    def test_delete_name(self):
        name = "name"
        expected_value = "123"

        class Parent(object):
            _example = {name: expected_value}

        instance = Parent()

        sot = TestComponent.ExampleComponent("name")

        sot.__delete__(instance)

        self.assertNotIn(name, instance._example)

    def test_delete_name_doesnt_exist(self):
        name = "name"
        expected_value = "123"

        class Parent(object):
            _example = {"what": expected_value}

        instance = Parent()

        sot = TestComponent.ExampleComponent(name)

        sot.__delete__(instance)

        self.assertNotIn(name, instance._example)


class TestComponentManager(base.TestCase):

    def test_create_basic(self):
        sot = resource._ComponentManager()
        self.assertEqual(dict(), sot.attributes)
        self.assertEqual(set(), sot._dirty)

    def test_create_unsynced(self):
        attrs = {"hey": 1, "hi": 2, "hello": 3}
        sync = False

        sot = resource._ComponentManager(attributes=attrs, synchronized=sync)
        self.assertEqual(attrs, sot.attributes)
        self.assertEqual(set(attrs.keys()), sot._dirty)

    def test_create_synced(self):
        attrs = {"hey": 1, "hi": 2, "hello": 3}
        sync = True

        sot = resource._ComponentManager(attributes=attrs, synchronized=sync)
        self.assertEqual(attrs, sot.attributes)
        self.assertEqual(set(), sot._dirty)

    def test_getitem(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource._ComponentManager(attributes=attrs)
        self.assertEqual(value, sot.__getitem__(key))

    def test_setitem_new(self):
        key = "key"
        value = "value"

        sot = resource._ComponentManager()
        sot.__setitem__(key, value)

        self.assertIn(key, sot.attributes)
        self.assertIn(key, sot.dirty)

    def test_setitem_unchanged(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource._ComponentManager(attributes=attrs, synchronized=True)
        # This shouldn't end up in the dirty list since we're just re-setting.
        sot.__setitem__(key, value)

        self.assertEqual(value, sot.attributes[key])
        self.assertNotIn(key, sot.dirty)

    def test_delitem(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource._ComponentManager(attributes=attrs, synchronized=True)
        sot.__delitem__(key)

        self.assertIsNone(sot.dirty[key])

    def test_iter(self):
        attrs = {"key": "value"}
        sot = resource._ComponentManager(attributes=attrs)
        self.assertItemsEqual(iter(attrs), sot.__iter__())

    def test_len(self):
        attrs = {"key": "value"}
        sot = resource._ComponentManager(attributes=attrs)
        self.assertEqual(len(attrs), sot.__len__())

    def test_dirty(self):
        key = "key"
        key2 = "key2"
        value = "value"
        attrs = {key: value}
        sot = resource._ComponentManager(attributes=attrs, synchronized=False)
        self.assertEqual({key: value}, sot.dirty)

        sot.__setitem__(key2, value)
        self.assertEqual({key: value, key2: value}, sot.dirty)

    def test_clean(self):
        key = "key"
        value = "value"
        attrs = {key: value}
        sot = resource._ComponentManager(attributes=attrs, synchronized=False)
        self.assertEqual(attrs, sot.dirty)

        sot.clean()

        self.assertEqual(dict(), sot.dirty)


class Test_Request(base.TestCase):

    def test_create(self):
        uri = 1
        body = 2
        headers = 3

        sot = resource._Request(uri, body, headers)

        self.assertEqual(uri, sot.url)
        self.assertEqual(body, sot.body)
        self.assertEqual(headers, sot.headers)


class TestQueryParameters(base.TestCase):

    def test_create(self):
        location = "location"
        mapping = {"first_name": "first-name"}

        sot = resource.QueryParameters(location, **mapping)

        self.assertEqual({"location": "location",
                          "first_name": "first-name",
                          "limit": "limit",
                          "marker": "marker"},
                         sot._mapping)

    def test_transpose_unmapped(self):
        location = "location"
        mapping = {"first_name": "first-name"}

        sot = resource.QueryParameters(location, **mapping)
        result = sot._transpose({"location": "Brooklyn",
                                 "first_name": "Brian",
                                 "last_name": "Curtin"})

        # last_name isn't mapped and shouldn't be included
        self.assertEqual({"location": "Brooklyn", "first-name": "Brian"},
                         result)

    def test_transpose_not_in_query(self):
        location = "location"
        mapping = {"first_name": "first-name"}

        sot = resource.QueryParameters(location, **mapping)
        result = sot._transpose({"location": "Brooklyn"})

        # first_name not being in the query shouldn't affect results
        self.assertEqual({"location": "Brooklyn"},
                         result)


class TestResource(base.TestCase):

    def test_initialize_basic(self):
        body = {"body": 1}
        header = {"header": 2, "Location": "somewhere"}
        uri = {"uri": 3}
        everything = dict(itertools.chain(body.items(), header.items(),
                                          uri.items()))

        mock_collect = mock.Mock()
        mock_collect.return_value = body, header, uri

        with mock.patch.object(resource.Resource,
                               "_collect_attrs", mock_collect):
            sot = resource.Resource(_synchronized=False, **everything)
            mock_collect.assert_called_once_with(everything)
        self.assertEqual("somewhere", sot.location)

        self.assertIsInstance(sot._body, resource._ComponentManager)
        self.assertEqual(body, sot._body.dirty)
        self.assertIsInstance(sot._header, resource._ComponentManager)
        self.assertEqual(header, sot._header.dirty)
        self.assertIsInstance(sot._uri, resource._ComponentManager)
        self.assertEqual(uri, sot._uri.dirty)

        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_head)
        self.assertEqual('PUT', sot.update_method)
        self.assertEqual('POST', sot.create_method)

    def test_repr(self):
        a = {"a": 1}
        b = {"b": 2}
        c = {"c": 3}

        class Test(resource.Resource):
            def __init__(self):
                self._body = mock.Mock()
                self._body.attributes.items = mock.Mock(
                    return_value=a.items())

                self._header = mock.Mock()
                self._header.attributes.items = mock.Mock(
                    return_value=b.items())

                self._uri = mock.Mock()
                self._uri.attributes.items = mock.Mock(
                    return_value=c.items())

        the_repr = repr(Test())

        # Don't test the arguments all together since the dictionary order
        # they're rendered in can't be depended on, nor does it matter.
        self.assertIn("openstack.tests.unit.test_resource.Test", the_repr)
        self.assertIn("a=1", the_repr)
        self.assertIn("b=2", the_repr)
        self.assertIn("c=3", the_repr)

    def test_equality(self):
        class Example(resource.Resource):
            x = resource.Body("x")
            y = resource.Header("y")
            z = resource.URI("z")

        e1 = Example(x=1, y=2, z=3)
        e2 = Example(x=1, y=2, z=3)
        e3 = Example(x=0, y=0, z=0)

        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test__update(self):
        sot = resource.Resource()

        body = "body"
        header = "header"
        uri = "uri"

        sot._collect_attrs = mock.Mock(return_value=(body, header, uri))
        sot._body.update = mock.Mock()
        sot._header.update = mock.Mock()
        sot._uri.update = mock.Mock()

        args = {"arg": 1}
        sot._update(**args)

        sot._collect_attrs.assert_called_once_with(args)
        sot._body.update.assert_called_once_with(body)
        sot._header.update.assert_called_once_with(header)
        sot._uri.update.assert_called_once_with(uri)

    def test__collect_attrs(self):
        sot = resource.Resource()

        expected_attrs = ["body", "header", "uri"]

        sot._consume_attrs = mock.Mock()
        sot._consume_attrs.side_effect = expected_attrs

        # It'll get passed an empty dict at the least.
        actual_attrs = sot._collect_attrs(dict())

        self.assertItemsEqual(expected_attrs, actual_attrs)

    def test__consume_attrs(self):
        serverside_key1 = "someKey1"
        clientside_key1 = "some_key1"
        serverside_key2 = "someKey2"
        clientside_key2 = "some_key2"
        value1 = "value1"
        value2 = "value2"
        mapping = {serverside_key1: clientside_key1,
                   serverside_key2: clientside_key2}

        other_key = "otherKey"
        other_value = "other"
        attrs = {clientside_key1: value1,
                 serverside_key2: value2,
                 other_key: other_value}

        sot = resource.Resource()

        result = sot._consume_attrs(mapping, attrs)

        # Make sure that the expected key was consumed and we're only
        # left with the other stuff.
        self.assertDictEqual({other_key: other_value}, attrs)

        # Make sure that after we've popped our relevant client-side
        # key off that we are returning it keyed off of its server-side
        # name.
        self.assertDictEqual({serverside_key1: value1,
                              serverside_key2: value2}, result)

    def test__mapping_defaults(self):
        # Check that even on an empty class, we get the expected
        # built-in attributes.

        self.assertIn("location", resource.Resource._header_mapping())
        self.assertIn("name", resource.Resource._body_mapping())
        self.assertIn("id", resource.Resource._body_mapping())

    def test__mapping_overrides(self):
        # Iterating through the MRO used to wipe out overrides of mappings
        # found in base classes.
        new_name = "MyName"
        new_id = "MyID"

        class Test(resource.Resource):
            name = resource.Body(new_name)
            id = resource.Body(new_id)

        mapping = Test._body_mapping()

        self.assertEqual("name", mapping["MyName"])
        self.assertEqual("id", mapping["MyID"])

    def test__body_mapping(self):
        class Test(resource.Resource):
            x = resource.Body("x")
            y = resource.Body("y")
            z = resource.Body("z")

        self.assertIn("x", Test._body_mapping())
        self.assertIn("y", Test._body_mapping())
        self.assertIn("z", Test._body_mapping())

    def test__header_mapping(self):
        class Test(resource.Resource):
            x = resource.Header("x")
            y = resource.Header("y")
            z = resource.Header("z")

        self.assertIn("x", Test._header_mapping())
        self.assertIn("y", Test._header_mapping())
        self.assertIn("z", Test._header_mapping())

    def test__uri_mapping(self):
        class Test(resource.Resource):
            x = resource.URI("x")
            y = resource.URI("y")
            z = resource.URI("z")

        self.assertIn("x", Test._uri_mapping())
        self.assertIn("y", Test._uri_mapping())
        self.assertIn("z", Test._uri_mapping())

    def test__getattribute__id_in_body(self):
        id = "lol"
        sot = resource.Resource(id=id)

        result = getattr(sot, "id")
        self.assertEqual(result, id)

    def test__getattribute__id_with_alternate(self):
        id = "lol"

        class Test(resource.Resource):
            blah = resource.Body("blah", alternate_id=True)

        sot = Test(blah=id)

        result = getattr(sot, "id")
        self.assertEqual(result, id)

    def test__getattribute__id_without_alternate(self):
        class Test(resource.Resource):
            id = None

        sot = Test()
        self.assertIsNone(sot.id)

    def test__alternate_id_None(self):
        self.assertEqual("", resource.Resource._alternate_id())

    def test__alternate_id(self):
        class Test(resource.Resource):
            alt = resource.Body("the_alt", alternate_id=True)

        self.assertTrue("the_alt", Test._alternate_id())

        value1 = "lol"
        sot = Test(alt=value1)
        self.assertEqual(sot.alt, value1)
        self.assertEqual(sot.id, value1)

        value2 = "rofl"
        sot = Test(the_alt=value2)
        self.assertEqual(sot.alt, value2)
        self.assertEqual(sot.id, value2)

    def test__get_id_instance(self):
        class Test(resource.Resource):
            id = resource.Body("id")

        value = "id"
        sot = Test(id=value)

        self.assertEqual(value, sot._get_id(sot))

    def test__get_id_instance_alternate(self):
        class Test(resource.Resource):
            attr = resource.Body("attr", alternate_id=True)

        value = "id"
        sot = Test(attr=value)

        self.assertEqual(value, sot._get_id(sot))

    def test__get_id_value(self):
        value = "id"
        self.assertEqual(value, resource.Resource._get_id(value))

    def test_to_dict(self):

        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'location': None,
            'foo': None,
            'bar': None
        }
        self.assertEqual(expected, res.to_dict())

    def test_to_dict_no_body(self):

        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        expected = {
            'location': None,
            'foo': None,
        }
        self.assertEqual(expected, res.to_dict(body=False))

    def test_to_dict_no_header(self):

        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'bar': None
        }
        self.assertEqual(expected, res.to_dict(headers=False))

    def test_to_dict_ignore_none(self):

        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID', bar='BAR')

        expected = {
            'id': 'FAKE_ID',
            'bar': 'BAR',
        }
        self.assertEqual(expected, res.to_dict(ignore_none=True))

    def test_to_dict_with_mro(self):

        class Parent(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        class Child(Parent):
            foo_new = resource.Header('foo_baz_server')
            bar_new = resource.Body('bar_baz_server')

        res = Child(id='FAKE_ID')

        expected = {
            'foo': None,
            'bar': None,
            'foo_new': None,
            'bar_new': None,
            'id': 'FAKE_ID',
            'location': None,
            'name': None
        }
        self.assertEqual(expected, res.to_dict())

    def test_to_dict_value_error(self):

        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        err = self.assertRaises(ValueError,
                                res.to_dict, body=False, headers=False)
        self.assertEqual('At least one of `body` or `headers` must be True',
                         six.text_type(err))

    def test_to_dict_with_mro_no_override(self):

        class Parent(resource.Resource):
            header = resource.Header('HEADER')
            body = resource.Body('BODY')

        class Child(Parent):
            # The following two properties are not supposed to be overridden
            # by the parent class property values.
            header = resource.Header('ANOTHER_HEADER')
            body = resource.Body('ANOTHER_BODY')

        res = Child(id='FAKE_ID', body='BODY_VALUE', header='HEADER_VALUE')

        expected = {
            'body': 'BODY_VALUE',
            'header': 'HEADER_VALUE',
            'id': 'FAKE_ID',
            'location': None,
            'name': None
        }
        self.assertEqual(expected, res.to_dict())

    def test_new(self):
        class Test(resource.Resource):
            attr = resource.Body("attr")

        value = "value"
        sot = Test.new(attr=value)

        self.assertIn("attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test_existing(self):
        class Test(resource.Resource):
            attr = resource.Body("attr")

        value = "value"
        sot = Test.existing(attr=value)

        self.assertNotIn("attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test__prepare_request_with_id(self):
        class Test(resource.Resource):
            base_path = "/something"
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        the_id = "id"
        body_value = "body"
        header_value = "header"
        sot = Test(id=the_id, body_attr=body_value, header_attr=header_value,
                   _synchronized=False)

        result = sot._prepare_request(requires_id=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual({"x": body_value, "id": the_id}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_missing_id(self):
        sot = resource.Resource(id=None)

        self.assertRaises(exceptions.InvalidRequest,
                          sot._prepare_request, requires_id=True)

    def test__prepare_request_with_key(self):
        key = "key"

        class Test(resource.Resource):
            base_path = "/something"
            resource_key = key
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        body_value = "body"
        header_value = "header"
        sot = Test(body_attr=body_value, header_attr=header_value,
                   _synchronized=False)

        result = sot._prepare_request(requires_id=False, prepend_key=True)

        self.assertEqual("/something", result.url)
        self.assertEqual({key: {"x": body_value}}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__translate_response_no_body(self):
        class Test(resource.Resource):
            attr = resource.Header("attr")

        response = FakeResponse({}, headers={"attr": "value"})

        sot = Test()

        sot._translate_response(response, has_body=False)

        self.assertEqual(dict(), sot._header.dirty)
        self.assertEqual("value", sot.attr)

    def test__translate_response_with_body_no_resource_key(self):
        class Test(resource.Resource):
            attr = resource.Body("attr")

        body = {"attr": "value"}
        response = FakeResponse(body)

        sot = Test()
        sot._filter_component = mock.Mock(side_effect=[body, dict()])

        sot._translate_response(response, has_body=True)

        self.assertEqual("value", sot.attr)
        self.assertEqual(dict(), sot._body.dirty)
        self.assertEqual(dict(), sot._header.dirty)

    def test__translate_response_with_body_with_resource_key(self):
        key = "key"

        class Test(resource.Resource):
            resource_key = key
            attr = resource.Body("attr")

        body = {"attr": "value"}
        response = FakeResponse({key: body})

        sot = Test()
        sot._filter_component = mock.Mock(side_effect=[body, dict()])

        sot._translate_response(response, has_body=True)

        self.assertEqual("value", sot.attr)
        self.assertEqual(dict(), sot._body.dirty)
        self.assertEqual(dict(), sot._header.dirty)

    def test_cant_do_anything(self):
        class Test(resource.Resource):
            allow_create = False
            allow_get = False
            allow_update = False
            allow_delete = False
            allow_head = False
            allow_list = False

        sot = Test()

        # The first argument to all of these operations is the session,
        # but we raise before we get to it so just pass anything in.
        self.assertRaises(exceptions.MethodNotSupported, sot.create, "")
        self.assertRaises(exceptions.MethodNotSupported, sot.get, "")
        self.assertRaises(exceptions.MethodNotSupported, sot.delete, "")
        self.assertRaises(exceptions.MethodNotSupported, sot.head, "")

        # list is a generator so you need to begin consuming
        # it in order to exercise the failure.
        the_list = sot.list("")
        self.assertRaises(exceptions.MethodNotSupported, next, the_list)

        # Update checks the dirty list first before even trying to see
        # if the call can be made, so fake a dirty list.
        sot._body = mock.Mock()
        sot._body.dirty = mock.Mock(return_value={"x": "y"})
        self.assertRaises(exceptions.MethodNotSupported, sot.update, "")


class TestResourceActions(base.TestCase):

    def setUp(self):
        super(TestResourceActions, self).setUp()

        self.service_name = "service"
        self.base_path = "base_path"

        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            resources_key = 'resources'
            allow_create = True
            allow_get = True
            allow_head = True
            allow_update = True
            allow_delete = True
            allow_list = True

        self.test_class = Test

        self.request = mock.Mock(spec=resource._Request)
        self.request.url = "uri"
        self.request.body = "body"
        self.request.headers = "headers"

        self.response = FakeResponse({})

        self.sot = Test(id="id")
        self.sot._prepare_request = mock.Mock(return_value=self.request)
        self.sot._translate_response = mock.Mock()

        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.create = mock.Mock(return_value=self.response)
        self.session.get = mock.Mock(return_value=self.response)
        self.session.put = mock.Mock(return_value=self.response)
        self.session.patch = mock.Mock(return_value=self.response)
        self.session.post = mock.Mock(return_value=self.response)
        self.session.delete = mock.Mock(return_value=self.response)
        self.session.head = mock.Mock(return_value=self.response)

    def _test_create(self, cls, requires_id=False, prepend_key=False):
        id = "id" if requires_id else None
        sot = cls(id=id)
        sot._prepare_request = mock.Mock(return_value=self.request)
        sot._translate_response = mock.Mock()

        result = sot.create(self.session, prepend_key=prepend_key)

        sot._prepare_request.assert_called_once_with(
            requires_id=requires_id, prepend_key=prepend_key)
        if requires_id:
            self.session.put.assert_called_once_with(
                self.request.url,
                json=self.request.body, headers=self.request.headers)
        else:
            self.session.post.assert_called_once_with(
                self.request.url,
                json=self.request.body, headers=self.request.headers)

        sot._translate_response.assert_called_once_with(self.response)
        self.assertEqual(result, sot)

    def test_put_create(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'PUT'

        self._test_create(Test, requires_id=True, prepend_key=True)

    def test_post_create(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'POST'

        self._test_create(Test, requires_id=False, prepend_key=True)

    def test_get(self):
        result = self.sot.get(self.session)

        self.sot._prepare_request.assert_called_once_with(requires_id=True)
        self.session.get.assert_called_once_with(
            self.request.url,)

        self.sot._translate_response.assert_called_once_with(self.response)
        self.assertEqual(result, self.sot)

    def test_get_not_requires_id(self):
        result = self.sot.get(self.session, False)

        self.sot._prepare_request.assert_called_once_with(requires_id=False)
        self.session.get.assert_called_once_with(
            self.request.url,)

        self.sot._translate_response.assert_called_once_with(self.response)
        self.assertEqual(result, self.sot)

    def test_head(self):
        result = self.sot.head(self.session)

        self.sot._prepare_request.assert_called_once_with()
        self.session.head.assert_called_once_with(
            self.request.url,
            headers={"Accept": ""})

        self.sot._translate_response.assert_called_once_with(
            self.response, has_body=False)
        self.assertEqual(result, self.sot)

    def _test_update(self, update_method='PUT', prepend_key=True,
                     has_body=True):
        self.sot.update_method = update_method

        # Need to make sot look dirty so we can attempt an update
        self.sot._body = mock.Mock()
        self.sot._body.dirty = mock.Mock(return_value={"x": "y"})

        self.sot.update(self.session, prepend_key=prepend_key,
                        has_body=has_body)

        self.sot._prepare_request.assert_called_once_with(
            prepend_key=prepend_key)

        if update_method == 'PATCH':
            self.session.patch.assert_called_once_with(
                self.request.url,
                json=self.request.body, headers=self.request.headers)
        elif update_method == 'POST':
            self.session.post.assert_called_once_with(
                self.request.url,
                json=self.request.body, headers=self.request.headers)
        elif update_method == 'PUT':
            self.session.put.assert_called_once_with(
                self.request.url,
                json=self.request.body, headers=self.request.headers)

        self.sot._translate_response.assert_called_once_with(
            self.response, has_body=has_body)

    def test_update_put(self):
        self._test_update(update_method='PUT', prepend_key=True, has_body=True)

    def test_update_patch(self):
        self._test_update(
            update_method='PATCH', prepend_key=False, has_body=False)

    def test_update_not_dirty(self):
        self.sot._body = mock.Mock()
        self.sot._body.dirty = dict()
        self.sot._header = mock.Mock()
        self.sot._header.dirty = dict()

        self.sot.update(self.session)

        self.session.put.assert_not_called()

    def test_delete(self):
        result = self.sot.delete(self.session)

        self.sot._prepare_request.assert_called_once_with()
        self.session.delete.assert_called_once_with(
            self.request.url,
            headers={"Accept": ""})

        self.sot._translate_response.assert_called_once_with(
            self.response, has_body=False)
        self.assertEqual(result, self.sot)

    # NOTE: As list returns a generator, testing it requires consuming
    # the generator. Wrap calls to self.sot.list in a `list`
    # and then test the results as a list of responses.
    def test_list_empty_response(self):
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"resources": []}

        self.session.get.return_value = mock_response

        result = list(self.sot.list(self.session))

        self.session.get.assert_called_once_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={})

        self.assertEqual([], result)

    def test_list_one_page_response_paginated(self):
        id_value = 1
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {"resources": [{"id": id_value}]}

        self.session.get.return_value = mock_response

        # Ensure that we break out of the loop on a paginated call
        # that still only results in one page of data.
        results = list(self.sot.list(self.session, paginated=True))

        self.assertEqual(1, len(results))

        self.assertEqual(1, len(self.session.get.call_args_list))
        self.assertEqual(id_value, results[0].id)
        self.assertIsInstance(results[0], self.test_class)

    def test_list_one_page_response_not_paginated(self):
        id_value = 1
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"resources": [{"id": id_value}]}

        self.session.get.return_value = mock_response

        results = list(self.sot.list(self.session, paginated=False))

        self.session.get.assert_called_once_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={})

        self.assertEqual(1, len(results))
        self.assertEqual(id_value, results[0].id)
        self.assertIsInstance(results[0], self.test_class)

    def test_list_one_page_response_resources_key(self):
        key = "resources"

        class Test(self.test_class):
            resources_key = key

        id_value = 1
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {key: [{"id": id_value}]}

        self.session.get.return_value = mock_response

        sot = Test()

        results = list(sot.list(self.session))

        self.session.get.assert_called_once_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={})

        self.assertEqual(1, len(results))
        self.assertEqual(id_value, results[0].id)
        self.assertIsInstance(results[0], self.test_class)

    def test_list_response_paginated_without_links(self):
        ids = [1, 2]
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {
            "resources": [{"id": ids[0]}],
            "resources_links": [{
                "href": "https://example.com/next-url",
                "rel": "next",
            }]
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.links = {}
        mock_response2.json.return_value = {
            "resources": [{"id": ids[1]}],
        }

        self.session.get.side_effect = [mock_response, mock_response2]

        results = list(self.sot.list(self.session, paginated=True))

        self.assertEqual(2, len(results))
        self.assertEqual(ids[0], results[0].id)
        self.assertEqual(ids[1], results[1].id)
        self.assertEqual(
            mock.call('base_path',
                      headers={'Accept': 'application/json'}, params={}),
            self.session.get.mock_calls[0])
        self.assertEqual(
            mock.call('https://example.com/next-url',
                      headers={'Accept': 'application/json'}, params={}),
            self.session.get.mock_calls[1])
        self.assertEqual(2, len(self.session.get.call_args_list))
        self.assertIsInstance(results[0], self.test_class)

    def test_list_response_paginated_with_links(self):
        ids = [1, 2]
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.side_effect = [
            {
                "resources": [{"id": ids[0]}],
                "resources_links": [{
                    "href": "https://example.com/next-url",
                    "rel": "next",
                }]
            }, {
                "resources": [{"id": ids[1]}],
            }]

        self.session.get.return_value = mock_response

        results = list(self.sot.list(self.session, paginated=True))

        self.assertEqual(2, len(results))
        self.assertEqual(ids[0], results[0].id)
        self.assertEqual(ids[1], results[1].id)
        self.assertEqual(
            mock.call('base_path',
                      headers={'Accept': 'application/json'}, params={}),
            self.session.get.mock_calls[0])
        self.assertEqual(
            mock.call('https://example.com/next-url',
                      headers={'Accept': 'application/json'}, params={}),
            self.session.get.mock_calls[2])
        self.assertEqual(2, len(self.session.get.call_args_list))
        self.assertIsInstance(results[0], self.test_class)

    def test_list_multi_page_response_not_paginated(self):
        ids = [1, 2]
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"resources": [{"id": ids[0]}]},
            {"resources": [{"id": ids[1]}]},
        ]

        self.session.get.return_value = mock_response

        results = list(self.sot.list(self.session, paginated=False))

        self.assertEqual(1, len(results))
        self.assertEqual(ids[0], results[0].id)
        self.assertIsInstance(results[0], self.test_class)

    def test_list_query_params(self):
        id = 1
        qp = "query param!"
        qp_name = "query-param"
        uri_param = "uri param!"

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {"resources": [{"id": id}]}

        mock_empty = mock.Mock()
        mock_empty.status_code = 200
        mock_empty.links = {}
        mock_empty.json.return_value = {"resources": []}

        self.session.get.side_effect = [mock_response, mock_empty]

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters(query_param=qp_name)
            base_path = "/%(something)s/blah"
            something = resource.URI("something")

        results = list(Test.list(self.session, paginated=True,
                                 query_param=qp, something=uri_param))

        self.assertEqual(1, len(results))

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.assertEqual(
            self.session.get.call_args_list[0][1]["params"],
            {qp_name: qp})

        self.assertEqual(self.session.get.call_args_list[0][0][0],
                         Test.base_path % {"something": uri_param})

    def test_invalid_list_params(self):
        id = 1
        qp = "query param!"
        qp_name = "query-param"
        uri_param = "uri param!"

        mock_response = mock.Mock()
        mock_response.json.side_effect = [[{"id": id}],
                                          []]

        self.session.get.return_value = mock_response

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters(query_param=qp_name)
            base_path = "/%(something)s/blah"
            something = resource.URI("something")

        try:
            list(Test.list(self.session, paginated=True, query_param=qp,
                           something=uri_param, something_wrong=True))
            self.assertFail('The above line should fail')
        except exceptions.InvalidResourceQuery as err:
            self.assertEqual(str(err), 'Invalid query params: something_wrong')

    def test_values_as_list_params(self):
        id = 1
        qp = "query param!"
        qp_name = "query-param"
        uri_param = "uri param!"

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {"resources": [{"id": id}]}

        mock_empty = mock.Mock()
        mock_empty.status_code = 200
        mock_empty.links = {}
        mock_empty.json.return_value = {"resources": []}

        self.session.get.side_effect = [mock_response, mock_empty]

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters(query_param=qp_name)
            base_path = "/%(something)s/blah"
            something = resource.URI("something")

        results = list(Test.list(self.session, paginated=True,
                       something=uri_param, **{qp_name: qp}))

        self.assertEqual(1, len(results))

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.assertEqual(
            self.session.get.call_args_list[0][1]["params"],
            {qp_name: qp})

        self.assertEqual(self.session.get.call_args_list[0][0][0],
                         Test.base_path % {"something": uri_param})

    def test_values_as_list_params_precedence(self):
        id = 1
        qp = "query param!"
        qp2 = "query param!!!!!"
        qp_name = "query-param"
        uri_param = "uri param!"

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {"resources": [{"id": id}]}

        mock_empty = mock.Mock()
        mock_empty.status_code = 200
        mock_empty.links = {}
        mock_empty.json.return_value = {"resources": []}

        self.session.get.side_effect = [mock_response, mock_empty]

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters(query_param=qp_name)
            base_path = "/%(something)s/blah"
            something = resource.URI("something")

        results = list(Test.list(self.session, paginated=True, query_param=qp2,
                       something=uri_param, **{qp_name: qp}))

        self.assertEqual(1, len(results))

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.assertEqual(
            self.session.get.call_args_list[0][1]["params"],
            {qp_name: qp2})

        self.assertEqual(self.session.get.call_args_list[0][0][0],
                         Test.base_path % {"something": uri_param})

    def test_list_multi_page_response_paginated(self):
        ids = [1, 2]
        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.links = {}
        resp1.json.return_value = {
            "resources": [{"id": ids[0]}],
            "resources_links": [{
                "href": "https://example.com/next-url",
                "rel": "next",
            }],
        }
        resp2 = mock.Mock()
        resp2.status_code = 200
        resp2.links = {}
        resp2.json.return_value = {
            "resources": [{"id": ids[1]}],
            "resources_links": [{
                "href": "https://example.com/next-url",
                "rel": "next",
            }],
        }
        resp3 = mock.Mock()
        resp3.status_code = 200
        resp3.links = {}
        resp3.json.return_value = {
            "resources": []
        }

        self.session.get.side_effect = [resp1, resp2, resp3]

        results = self.sot.list(self.session, paginated=True)

        result0 = next(results)
        self.assertEqual(result0.id, ids[0])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={})

        result1 = next(results)
        self.assertEqual(result1.id, ids[1])
        self.session.get.assert_called_with(
            'https://example.com/next-url',
            headers={"Accept": "application/json"},
            params={})

        self.assertRaises(StopIteration, next, results)
        self.session.get.assert_called_with(
            'https://example.com/next-url',
            headers={"Accept": "application/json"},
            params={})

    def test_list_multi_page_no_early_termination(self):
        # This tests verifies that multipages are not early terminated.
        # APIs can set max_limit to the number of items returned in each
        # query. If that max_limit is smaller than the limit given by the
        # user, the return value would contain less items than the limit,
        # but that doesn't stand to reason that there are no more records,
        # we should keep trying to get more results.
        ids = [1, 2, 3, 4]
        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.links = {}
        resp1.json.return_value = {
            # API's max_limit is set to 2.
            "resources": [{"id": ids[0]}, {"id": ids[1]}],
        }
        resp2 = mock.Mock()
        resp2.status_code = 200
        resp2.links = {}
        resp2.json.return_value = {
            # API's max_limit is set to 2.
            "resources": [{"id": ids[2]}, {"id": ids[3]}],
        }
        resp3 = mock.Mock()
        resp3.status_code = 200
        resp3.json.return_value = {
            "resources": [],
        }

        self.session.get.side_effect = [resp1, resp2, resp3]

        results = self.sot.list(self.session, limit=3, paginated=True)

        # First page constains only two items, less than the limit given
        result0 = next(results)
        self.assertEqual(result0.id, ids[0])
        result1 = next(results)
        self.assertEqual(result1.id, ids[1])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={"limit": 3})

        # Second page contains another two items
        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        result3 = next(results)
        self.assertEqual(result3.id, ids[3])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={"limit": 3, "marker": 2})

        # Ensure we're done after those four items
        self.assertRaises(StopIteration, next, results)

        # Ensure we've given the last try to get more results
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={"limit": 3, "marker": 4})

        # Ensure we made three calls to get this done
        self.assertEqual(3, len(self.session.get.call_args_list))

    def test_list_multi_page_inferred_additional(self):
        # If we explicitly request a limit and we receive EXACTLY that
        # amount of results and there is no next link, we make one additional
        # call to check to see if there are more records and the service is
        # just sad.
        # NOTE(mordred) In a perfect world we would not do this. But it's 2018
        # and I don't think anyone has any illusions that we live in a perfect
        # world anymore.
        ids = [1, 2, 3]
        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.links = {}
        resp1.json.return_value = {
            "resources": [{"id": ids[0]}, {"id": ids[1]}],
        }
        resp2 = mock.Mock()
        resp2.status_code = 200
        resp2.links = {}
        resp2.json.return_value = {"resources": [{"id": ids[2]}]}

        self.session.get.side_effect = [resp1, resp2]

        results = self.sot.list(self.session, limit=2, paginated=True)

        # Get the first page's two items
        result0 = next(results)
        self.assertEqual(result0.id, ids[0])
        result1 = next(results)
        self.assertEqual(result1.id, ids[1])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={"limit": 2})

        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={'limit': 2, 'marker': 2})

        # Ensure we're done after those three items
        self.assertRaises(StopIteration, next, results)

        # Ensure we only made two calls to get this done
        self.assertEqual(3, len(self.session.get.call_args_list))

    def test_list_multi_page_header_count(self):
        class Test(self.test_class):
            resources_key = None
            pagination_key = 'X-Container-Object-Count'
        self.sot = Test()

        # Swift returns a total number of objects in a header and we compare
        # that against the total number returned to know if we need to fetch
        # more objects.
        ids = [1, 2, 3]
        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.links = {}
        resp1.headers = {'X-Container-Object-Count': 3}
        resp1.json.return_value = [{"id": ids[0]}, {"id": ids[1]}]
        resp2 = mock.Mock()
        resp2.status_code = 200
        resp2.links = {}
        resp2.headers = {'X-Container-Object-Count': 3}
        resp2.json.return_value = [{"id": ids[2]}]

        self.session.get.side_effect = [resp1, resp2]

        results = self.sot.list(self.session, paginated=True)

        # Get the first page's two items
        result0 = next(results)
        self.assertEqual(result0.id, ids[0])
        result1 = next(results)
        self.assertEqual(result1.id, ids[1])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={})

        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={'marker': 2})

        # Ensure we're done after those three items
        self.assertRaises(StopIteration, next, results)

        # Ensure we only made two calls to get this done
        self.assertEqual(2, len(self.session.get.call_args_list))

    def test_list_multi_page_link_header(self):
        # Swift returns a total number of objects in a header and we compare
        # that against the total number returned to know if we need to fetch
        # more objects.
        ids = [1, 2, 3]
        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.links = {
            'next': {'uri': 'https://example.com/next-url', 'rel': 'next'}}
        resp1.headers = {}
        resp1.json.return_value = {
            "resources": [{"id": ids[0]}, {"id": ids[1]}],
        }
        resp2 = mock.Mock()
        resp2.status_code = 200
        resp2.links = {}
        resp2.headers = {}
        resp2.json.return_value = {"resources": [{"id": ids[2]}]}

        self.session.get.side_effect = [resp1, resp2]

        results = self.sot.list(self.session, paginated=True)

        # Get the first page's two items
        result0 = next(results)
        self.assertEqual(result0.id, ids[0])
        result1 = next(results)
        self.assertEqual(result1.id, ids[1])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={})

        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        self.session.get.assert_called_with(
            'https://example.com/next-url',
            headers={"Accept": "application/json"},
            params={})

        # Ensure we're done after those three items
        self.assertRaises(StopIteration, next, results)

        # Ensure we only made two calls to get this done
        self.assertEqual(2, len(self.session.get.call_args_list))


class TestResourceFind(base.TestCase):

    def setUp(self):
        super(TestResourceFind, self).setUp()

        self.result = 1

        class Base(resource.Resource):

            @classmethod
            def existing(cls, **kwargs):
                response = mock.Mock()
                response.status_code = 404
                raise exceptions.NotFoundException(
                    'Not Found', response=response)

            @classmethod
            def list(cls, session):
                return None

        class OneResult(Base):

            @classmethod
            def _get_one_match(cls, *args):
                return self.result

        class NoResults(Base):

            @classmethod
            def _get_one_match(cls, *args):
                return None

        self.no_results = NoResults
        self.one_result = OneResult

    def test_find_short_circuit(self):
        value = 1

        class Test(resource.Resource):

            @classmethod
            def existing(cls, **kwargs):
                mock_match = mock.Mock()
                mock_match.get.return_value = value
                return mock_match

        result = Test.find("session", "name")

        self.assertEqual(result, value)

    def test_no_match_raise(self):
        self.assertRaises(exceptions.ResourceNotFound, self.no_results.find,
                          "session", "name", ignore_missing=False)

    def test_no_match_return(self):
        self.assertIsNone(
            self.no_results.find("session", "name", ignore_missing=True))

    def test_find_result(self):
        self.assertEqual(self.result, self.one_result.find("session", "name"))

    def test_match_empty_results(self):
        self.assertIsNone(resource.Resource._get_one_match("name", []))

    def test_no_match_by_name(self):
        the_name = "Brian"

        match = mock.Mock(spec=resource.Resource)
        match.name = the_name

        result = resource.Resource._get_one_match("Richard", [match])

        self.assertIsNone(result, match)

    def test_single_match_by_name(self):
        the_name = "Brian"

        match = mock.Mock(spec=resource.Resource)
        match.name = the_name

        result = resource.Resource._get_one_match(the_name, [match])

        self.assertIs(result, match)

    def test_single_match_by_id(self):
        the_id = "Brian"

        match = mock.Mock(spec=resource.Resource)
        match.id = the_id

        result = resource.Resource._get_one_match(the_id, [match])

        self.assertIs(result, match)

    def test_single_match_by_alternate_id(self):
        the_id = "Richard"

        class Test(resource.Resource):
            other_id = resource.Body("other_id", alternate_id=True)

        match = Test(other_id=the_id)
        result = Test._get_one_match(the_id, [match])

        self.assertIs(result, match)

    def test_multiple_matches(self):
        the_id = "Brian"

        match = mock.Mock(spec=resource.Resource)
        match.id = the_id

        self.assertRaises(
            exceptions.DuplicateResource,
            resource.Resource._get_one_match, the_id, [match, match])


class TestWaitForStatus(base.TestCase):

    def test_immediate_status(self):
        status = "loling"
        res = mock.Mock()
        res.status = status

        result = resource.wait_for_status(
            "session", res, status, "failures", "interval", "wait")

        self.assertTrue(result, res)

    def _resources_from_statuses(self, *statuses):
        resources = []
        for status in statuses:
            res = mock.Mock()
            res.status = status
            resources.append(res)
        for index, res in enumerate(resources[:-1]):
            res.get.return_value = resources[index + 1]
        return resources

    def test_status_match(self):
        status = "loling"

        # other gets past the first check, two anothers gets through
        # the sleep loop, and the third matches
        resources = self._resources_from_statuses(
            "first", "other", "another", "another", status)

        result = resource.wait_for_status(
            mock.Mock(), resources[0], status, None, 1, 5)

        self.assertEqual(result, resources[-1])

    def test_status_fails(self):
        failure = "crying"

        resources = self._resources_from_statuses("success", "other", failure)

        self.assertRaises(
            exceptions.ResourceFailure,
            resource.wait_for_status,
            mock.Mock(), resources[0], "loling", [failure], 1, 5)

    def test_timeout(self):
        status = "loling"
        res = mock.Mock()

        # The first "other" gets past the first check, and then three
        # pairs of "other" statuses run through the sleep counter loop,
        # after which time should be up. This is because we have a
        # one second interval and three second waiting period.
        statuses = ["other"] * 7
        type(res).status = mock.PropertyMock(side_effect=statuses)

        self.assertRaises(exceptions.ResourceTimeout,
                          resource.wait_for_status,
                          "session", res, status, None, 0.01, 0.1)

    def test_no_sleep(self):
        res = mock.Mock()
        statuses = ["other"]
        type(res).status = mock.PropertyMock(side_effect=statuses)

        self.assertRaises(exceptions.ResourceTimeout,
                          resource.wait_for_status,
                          "session", res, "status", None, 0, -1)


class TestWaitForDelete(base.TestCase):

    def test_success(self):
        response = mock.Mock()
        response.headers = {}
        response.status_code = 404
        res = mock.Mock()
        res.get.side_effect = [
            None, None,
            exceptions.NotFoundException('Not Found', response)]

        result = resource.wait_for_delete("session", res, 1, 3)

        self.assertEqual(result, res)

    def test_timeout(self):
        res = mock.Mock()
        res.status = 'ACTIVE'
        res.get.return_value = res

        self.assertRaises(
            exceptions.ResourceTimeout,
            resource.wait_for_delete,
            "session", res, 0.1, 0.3)
