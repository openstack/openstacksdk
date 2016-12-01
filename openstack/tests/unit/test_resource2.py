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

import mock
import six

from openstack import exceptions
from openstack import format
from openstack import resource2
from openstack import session
from openstack.tests.unit import base


class TestComponent(base.TestCase):

    class ExampleComponent(resource2._BaseComponent):
        key = "_example"

    # Since we're testing ExampleComponent, which is as isolated as we
    # can test _BaseComponent due to it's needing to be a data member
    # of a class that has an attribute on the parent class named `key`,
    # each test has to implement a class with a name that is the same
    # as ExampleComponent.key, which should be a dict containing the
    # keys and values to test against.

    def test_implementations(self):
        self.assertEqual("_body", resource2.Body.key)
        self.assertEqual("_header", resource2.Header.key)
        self.assertEqual("_uri", resource2.URI.key)

    def test_creation(self):
        sot = resource2._BaseComponent("name", type=int, default=1,
                                       alternate_id=True)

        self.assertEqual("name", sot.name)
        self.assertEqual(int, sot.type)
        self.assertEqual(1, sot.default)
        self.assertTrue(sot.alternate_id)

    def test_get_no_instance(self):
        sot = resource2._BaseComponent("test")

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

        class FakeFormatter(object):
            @classmethod
            def deserialize(cls, value):
                return expected_result

        instance = Parent()
        sot = TestComponent.ExampleComponent("name", type=FakeFormatter)

        # Mock out issubclass rather than having an actual format.Formatter
        # This can't be mocked via decorator, isolate it to wrapping the call.
        mock_issubclass = mock.Mock(return_value=True)
        module = six.moves.builtins.__name__
        with mock.patch("%s.issubclass" % module, mock_issubclass):
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
        sot = resource2._ComponentManager()
        self.assertEqual(dict(), sot.attributes)
        self.assertEqual(set(), sot._dirty)

    def test_create_unsynced(self):
        attrs = {"hey": 1, "hi": 2, "hello": 3}
        sync = False

        sot = resource2._ComponentManager(attributes=attrs, synchronized=sync)
        self.assertEqual(attrs, sot.attributes)
        self.assertEqual(set(attrs.keys()), sot._dirty)

    def test_create_synced(self):
        attrs = {"hey": 1, "hi": 2, "hello": 3}
        sync = True

        sot = resource2._ComponentManager(attributes=attrs, synchronized=sync)
        self.assertEqual(attrs, sot.attributes)
        self.assertEqual(set(), sot._dirty)

    def test_getitem(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource2._ComponentManager(attributes=attrs)
        self.assertEqual(value, sot.__getitem__(key))

    def test_setitem_new(self):
        key = "key"
        value = "value"

        sot = resource2._ComponentManager()
        sot.__setitem__(key, value)

        self.assertIn(key, sot.attributes)
        self.assertIn(key, sot.dirty)

    def test_setitem_unchanged(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource2._ComponentManager(attributes=attrs, synchronized=True)
        # This shouldn't end up in the dirty list since we're just re-setting.
        sot.__setitem__(key, value)

        self.assertEqual(value, sot.attributes[key])
        self.assertNotIn(key, sot.dirty)

    def test_delitem(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource2._ComponentManager(attributes=attrs, synchronized=True)
        sot.__delitem__(key)

        self.assertIsNone(sot.dirty[key])

    def test_iter(self):
        attrs = {"key": "value"}
        sot = resource2._ComponentManager(attributes=attrs)
        self.assertItemsEqual(iter(attrs), sot.__iter__())

    def test_len(self):
        attrs = {"key": "value"}
        sot = resource2._ComponentManager(attributes=attrs)
        self.assertEqual(len(attrs), sot.__len__())

    def test_dirty(self):
        key = "key"
        key2 = "key2"
        value = "value"
        attrs = {key: value}
        sot = resource2._ComponentManager(attributes=attrs, synchronized=False)
        self.assertEqual({key: value}, sot.dirty)

        sot.__setitem__(key2, value)
        self.assertEqual({key: value, key2: value}, sot.dirty)

    def test_clean(self):
        key = "key"
        value = "value"
        attrs = {key: value}
        sot = resource2._ComponentManager(attributes=attrs, synchronized=False)
        self.assertEqual(attrs, sot.dirty)

        sot.clean()

        self.assertEqual(dict(), sot.dirty)


class Test_Request(base.TestCase):

    def test_create(self):
        uri = 1
        body = 2
        headers = 3

        sot = resource2._Request(uri, body, headers)

        self.assertEqual(uri, sot.uri)
        self.assertEqual(body, sot.body)
        self.assertEqual(headers, sot.headers)


class TestQueryParameters(base.TestCase):

    def test_create(self):
        location = "location"
        mapping = {"first_name": "first-name"}

        sot = resource2.QueryParameters(location, **mapping)

        self.assertEqual({"location": "location",
                          "first_name": "first-name",
                          "limit": "limit",
                          "marker": "marker"},
                         sot._mapping)

    def test_transpose_unmapped(self):
        location = "location"
        mapping = {"first_name": "first-name"}

        sot = resource2.QueryParameters(location, **mapping)
        result = sot._transpose({"location": "Brooklyn",
                                 "first_name": "Brian",
                                 "last_name": "Curtin"})

        # last_name isn't mapped and shouldn't be included
        self.assertEqual({"location": "Brooklyn", "first-name": "Brian"},
                         result)

    def test_transpose_not_in_query(self):
        location = "location"
        mapping = {"first_name": "first-name"}

        sot = resource2.QueryParameters(location, **mapping)
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

        with mock.patch.object(resource2.Resource,
                               "_collect_attrs", mock_collect):
            sot = resource2.Resource(_synchronized=False, **everything)
            mock_collect.assert_called_once_with(everything)
        self.assertEqual("somewhere", sot.location)

        self.assertIsInstance(sot._body, resource2._ComponentManager)
        self.assertEqual(body, sot._body.dirty)
        self.assertIsInstance(sot._header, resource2._ComponentManager)
        self.assertEqual(header, sot._header.dirty)
        self.assertIsInstance(sot._uri, resource2._ComponentManager)
        self.assertEqual(uri, sot._uri.dirty)

        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_head)
        self.assertFalse(sot.patch_update)
        self.assertFalse(sot.put_create)

    def test_repr(self):
        a = {"a": 1}
        b = {"b": 2}
        c = {"c": 3}

        class Test(resource2.Resource):
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
        self.assertIn("openstack.tests.unit.test_resource2.Test", the_repr)
        self.assertIn("a=1", the_repr)
        self.assertIn("b=2", the_repr)
        self.assertIn("c=3", the_repr)

    def test_equality(self):
        class Example(resource2.Resource):
            x = resource2.Body("x")
            y = resource2.Header("y")
            z = resource2.URI("z")

        e1 = Example(x=1, y=2, z=3)
        e2 = Example(x=1, y=2, z=3)
        e3 = Example(x=0, y=0, z=0)

        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)

    def test__update(self):
        sot = resource2.Resource()

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
        sot = resource2.Resource()

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
        mapping = {clientside_key1: serverside_key1,
                   clientside_key2: serverside_key2}

        other_key = "otherKey"
        other_value = "other"
        attrs = {clientside_key1: value1,
                 serverside_key2: value2,
                 other_key: other_value}

        sot = resource2.Resource()

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

        self.assertIn("location", resource2.Resource._header_mapping())
        self.assertIn("name", resource2.Resource._body_mapping())
        self.assertIn("id", resource2.Resource._body_mapping())

    def test__mapping_overrides(self):
        # Iterating through the MRO used to wipe out overrides of mappings
        # found in base classes.
        new_name = "MyName"
        new_id = "MyID"

        class Test(resource2.Resource):
            name = resource2.Body(new_name)
            id = resource2.Body(new_id)

        mapping = Test._body_mapping()

        self.assertEqual(new_name, mapping["name"])
        self.assertEqual(new_id, mapping["id"])

    def test__body_mapping(self):
        class Test(resource2.Resource):
            x = resource2.Body("x")
            y = resource2.Body("y")
            z = resource2.Body("z")

        self.assertIn("x", Test._body_mapping())
        self.assertIn("y", Test._body_mapping())
        self.assertIn("z", Test._body_mapping())

    def test__header_mapping(self):
        class Test(resource2.Resource):
            x = resource2.Header("x")
            y = resource2.Header("y")
            z = resource2.Header("z")

        self.assertIn("x", Test._header_mapping())
        self.assertIn("y", Test._header_mapping())
        self.assertIn("z", Test._header_mapping())

    def test__uri_mapping(self):
        class Test(resource2.Resource):
            x = resource2.URI("x")
            y = resource2.URI("y")
            z = resource2.URI("z")

        self.assertIn("x", Test._uri_mapping())
        self.assertIn("y", Test._uri_mapping())
        self.assertIn("z", Test._uri_mapping())

    def test__getattribute__id_in_body(self):
        id = "lol"
        sot = resource2.Resource(id=id)

        result = getattr(sot, "id")
        self.assertEqual(result, id)

    def test__getattribute__id_with_alternate(self):
        id = "lol"

        class Test(resource2.Resource):
            blah = resource2.Body("blah", alternate_id=True)

        sot = Test(blah=id)

        result = getattr(sot, "id")
        self.assertEqual(result, id)

    def test__getattribute__id_without_alternate(self):
        class Test(resource2.Resource):
            id = None

        sot = Test()
        self.assertIsNone(sot.id)

    def test__alternate_id_None(self):
        self.assertEqual("", resource2.Resource._alternate_id())

    def test__alternate_id(self):
        class Test(resource2.Resource):
            alt = resource2.Body("the_alt", alternate_id=True)

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
        class Test(resource2.Resource):
            id = resource2.Body("id")

        value = "id"
        sot = Test(id=value)

        self.assertEqual(value, sot._get_id(sot))

    def test__get_id_instance_alternate(self):
        class Test(resource2.Resource):
            attr = resource2.Body("attr", alternate_id=True)

        value = "id"
        sot = Test(attr=value)

        self.assertEqual(value, sot._get_id(sot))

    def test__get_id_value(self):
        value = "id"
        self.assertEqual(value, resource2.Resource._get_id(value))

    def test_to_dict(self):

        class Test(resource2.Resource):
            foo = resource2.Header('foo')
            bar = resource2.Body('bar')

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

        class Test(resource2.Resource):
            foo = resource2.Header('foo')
            bar = resource2.Body('bar')

        res = Test(id='FAKE_ID')

        expected = {
            'location': None,
            'foo': None,
        }
        self.assertEqual(expected, res.to_dict(body=False))

    def test_to_dict_no_header(self):

        class Test(resource2.Resource):
            foo = resource2.Header('foo')
            bar = resource2.Body('bar')

        res = Test(id='FAKE_ID')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'bar': None
        }
        self.assertEqual(expected, res.to_dict(headers=False))

    def test_to_dict_ignore_none(self):

        class Test(resource2.Resource):
            foo = resource2.Header('foo')
            bar = resource2.Body('bar')

        res = Test(id='FAKE_ID', bar='BAR')

        expected = {
            'id': 'FAKE_ID',
            'bar': 'BAR',
        }
        self.assertEqual(expected, res.to_dict(ignore_none=True))

    def test_to_dict_with_mro(self):

        class Parent(resource2.Resource):
            foo = resource2.Header('foo')
            bar = resource2.Body('bar')

        class Child(Parent):
            foo_new = resource2.Header('foo_baz_server')
            bar_new = resource2.Body('bar_baz_server')

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

        class Test(resource2.Resource):
            foo = resource2.Header('foo')
            bar = resource2.Body('bar')

        res = Test(id='FAKE_ID')

        err = self.assertRaises(ValueError,
                                res.to_dict, body=False, headers=False)
        self.assertEqual('At least one of `body` or `headers` must be True',
                         six.text_type(err))

    def test_to_dict_with_mro_no_override(self):

        class Parent(resource2.Resource):
            header = resource2.Header('HEADER')
            body = resource2.Body('BODY')

        class Child(Parent):
            # The following two properties are not supposed to be overridden
            # by the parent class property values.
            header = resource2.Header('ANOTHER_HEADER')
            body = resource2.Body('ANOTHER_BODY')

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
        class Test(resource2.Resource):
            attr = resource2.Body("attr")

        value = "value"
        sot = Test.new(attr=value)

        self.assertIn("attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test_existing(self):
        class Test(resource2.Resource):
            attr = resource2.Body("attr")

        value = "value"
        sot = Test.existing(attr=value)

        self.assertNotIn("attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test__prepare_request_with_id(self):
        class Test(resource2.Resource):
            base_path = "/something"
            body_attr = resource2.Body("x")
            header_attr = resource2.Header("y")

        the_id = "id"
        body_value = "body"
        header_value = "header"
        sot = Test(id=the_id, body_attr=body_value, header_attr=header_value,
                   _synchronized=False)

        result = sot._prepare_request(requires_id=True)

        self.assertEqual("something/id", result.uri)
        self.assertEqual({"x": body_value, "id": the_id}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_missing_id(self):
        sot = resource2.Resource(id=None)

        self.assertRaises(exceptions.InvalidRequest,
                          sot._prepare_request, requires_id=True)

    def test__prepare_request_with_key(self):
        key = "key"

        class Test(resource2.Resource):
            base_path = "/something"
            resource_key = key
            body_attr = resource2.Body("x")
            header_attr = resource2.Header("y")

        body_value = "body"
        header_value = "header"
        sot = Test(body_attr=body_value, header_attr=header_value,
                   _synchronized=False)

        result = sot._prepare_request(requires_id=False, prepend_key=True)

        self.assertEqual("/something", result.uri)
        self.assertEqual({key: {"x": body_value}}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__filter_component(self):
        client_name = "client_name"
        server_name = "serverName"
        value = "value"
        # Include something in the mapping that we don't receive
        # so the branch that looks at existence in the compoment is checked.
        mapping = {client_name: server_name, "other": "blah"}
        component = {server_name: value, "something": "else"}

        sot = resource2.Resource()
        result = sot._filter_component(component, mapping)

        # The something:else mapping should not make it into here.
        self.assertEqual({server_name: value}, result)

    def test__translate_response_no_body(self):
        class Test(resource2.Resource):
            attr = resource2.Header("attr")

        response = mock.Mock()
        response.headers = dict()

        sot = Test()
        sot._filter_component = mock.Mock(return_value={"attr": "value"})

        sot._translate_response(response, has_body=False)

        self.assertEqual(dict(), sot._header.dirty)
        self.assertEqual("value", sot.attr)

    def test__translate_response_with_body_no_resource_key(self):
        class Test(resource2.Resource):
            attr = resource2.Body("attr")

        body = {"attr": "value"}
        response = mock.Mock()
        response.headers = dict()
        response.json.return_value = body

        sot = Test()
        sot._filter_component = mock.Mock(side_effect=[body, dict()])

        sot._translate_response(response, has_body=True)

        self.assertEqual("value", sot.attr)
        self.assertEqual(dict(), sot._body.dirty)
        self.assertEqual(dict(), sot._header.dirty)

    def test__translate_response_with_body_with_resource_key(self):
        key = "key"

        class Test(resource2.Resource):
            resource_key = key
            attr = resource2.Body("attr")

        body = {"attr": "value"}
        response = mock.Mock()
        response.headers = dict()
        response.json.return_value = {key: body}

        sot = Test()
        sot._filter_component = mock.Mock(side_effect=[body, dict()])

        sot._translate_response(response, has_body=True)

        self.assertEqual("value", sot.attr)
        self.assertEqual(dict(), sot._body.dirty)
        self.assertEqual(dict(), sot._header.dirty)

    def test_cant_do_anything(self):
        class Test(resource2.Resource):
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

        class Test(resource2.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            allow_get = True
            allow_head = True
            allow_update = True
            allow_delete = True
            allow_list = True

        self.test_class = Test

        self.request = mock.Mock(spec=resource2._Request)
        self.request.uri = "uri"
        self.request.body = "body"
        self.request.headers = "headers"

        self.response = mock.Mock()

        self.sot = Test(id="id")
        self.sot._prepare_request = mock.Mock(return_value=self.request)
        self.sot._translate_response = mock.Mock()

        self.session = mock.Mock(spec=session.Session)
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
                self.request.uri,
                endpoint_filter=self.service_name,
                json=self.request.body, headers=self.request.headers)
        else:
            self.session.post.assert_called_once_with(
                self.request.uri,
                endpoint_filter=self.service_name,
                json=self.request.body, headers=self.request.headers)

        sot._translate_response.assert_called_once_with(self.response)
        self.assertEqual(result, sot)

    def test_put_create(self):
        class Test(resource2.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            put_create = True

        self._test_create(Test, requires_id=True, prepend_key=True)

    def test_post_create(self):
        class Test(resource2.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            put_create = False

        self._test_create(Test, requires_id=False, prepend_key=True)

    def test_get(self):
        result = self.sot.get(self.session)

        self.sot._prepare_request.assert_called_once_with(requires_id=True)
        self.session.get.assert_called_once_with(
            self.request.uri, endpoint_filter=self.service_name)

        self.sot._translate_response.assert_called_once_with(self.response)
        self.assertEqual(result, self.sot)

    def test_get_not_requires_id(self):
        result = self.sot.get(self.session, False)

        self.sot._prepare_request.assert_called_once_with(requires_id=False)
        self.session.get.assert_called_once_with(
            self.request.uri, endpoint_filter=self.service_name)

        self.sot._translate_response.assert_called_once_with(self.response)
        self.assertEqual(result, self.sot)

    def test_head(self):
        result = self.sot.head(self.session)

        self.sot._prepare_request.assert_called_once_with()
        self.session.head.assert_called_once_with(
            self.request.uri,
            endpoint_filter=self.service_name,
            headers={"Accept": ""})

        self.sot._translate_response.assert_called_once_with(self.response)
        self.assertEqual(result, self.sot)

    def _test_update(self, patch_update=False, prepend_key=True,
                     has_body=True):
        self.sot.patch_update = patch_update

        # Need to make sot look dirty so we can attempt an update
        self.sot._body = mock.Mock()
        self.sot._body.dirty = mock.Mock(return_value={"x": "y"})

        self.sot.update(self.session, prepend_key=prepend_key,
                        has_body=has_body)

        self.sot._prepare_request.assert_called_once_with(
            prepend_key=prepend_key)

        if patch_update:
            self.session.patch.assert_called_once_with(
                self.request.uri,
                endpoint_filter=self.service_name,
                json=self.request.body, headers=self.request.headers)
        else:
            self.session.put.assert_called_once_with(
                self.request.uri,
                endpoint_filter=self.service_name,
                json=self.request.body, headers=self.request.headers)

        self.sot._translate_response.assert_called_once_with(
            self.response, has_body=has_body)

    def test_update_put(self):
        self._test_update(patch_update=False, prepend_key=True, has_body=True)

    def test_update_patch(self):
        self._test_update(patch_update=True, prepend_key=False, has_body=False)

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
            self.request.uri,
            endpoint_filter=self.service_name,
            headers={"Accept": ""})

        self.sot._translate_response.assert_called_once_with(
            self.response, has_body=False)
        self.assertEqual(result, self.sot)

    # NOTE: As list returns a generator, testing it requires consuming
    # the generator. Wrap calls to self.sot.list in a `list`
    # and then test the results as a list of responses.
    def test_list_empty_response(self):
        mock_response = mock.Mock()
        mock_response.json.return_value = []

        self.session.get.return_value = mock_response

        result = list(self.sot.list(self.session))

        self.session.get.assert_called_once_with(
            self.base_path,
            endpoint_filter=self.service_name,
            headers={"Accept": "application/json"},
            params={})

        self.assertEqual([], result)

    def test_list_one_page_response_paginated(self):
        id_value = 1
        mock_response = mock.Mock()
        mock_response.json.side_effect = [[{"id": id_value}],
                                          []]

        self.session.get.return_value = mock_response

        # Ensure that we break out of the loop on a paginated call
        # that still only results in one page of data.
        results = list(self.sot.list(self.session, paginated=True))

        self.assertEqual(1, len(results))

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.session.get.call_args_list[0][1]["params"] = {}
        self.session.get.call_args_list[1][1]["params"] = {"marker": id_value}
        self.assertEqual(id_value, results[0].id)
        self.assertIsInstance(results[0], self.test_class)

    def test_list_one_page_response_not_paginated(self):
        id_value = 1
        mock_response = mock.Mock()
        mock_response.json.return_value = [{"id": id_value}]

        self.session.get.return_value = mock_response

        results = list(self.sot.list(self.session, paginated=False))

        self.session.get.assert_called_once_with(
            self.base_path,
            endpoint_filter=self.service_name,
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
        mock_response.json.return_value = {key: [{"id": id_value}]}

        self.session.get.return_value = mock_response

        sot = Test()

        results = list(sot.list(self.session))

        self.session.get.assert_called_once_with(
            self.base_path,
            endpoint_filter=self.service_name,
            headers={"Accept": "application/json"},
            params={})

        self.assertEqual(1, len(results))
        self.assertEqual(id_value, results[0].id)
        self.assertIsInstance(results[0], self.test_class)

    def test_list_multi_page_response_not_paginated(self):
        ids = [1, 2]
        mock_response = mock.Mock()
        mock_response.json.side_effect = [[{"id": ids[0]}],
                                          [{"id": ids[1]}]]

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
        mock_response.json.side_effect = [[{"id": id}],
                                          []]

        self.session.get.return_value = mock_response

        class Test(self.test_class):
            _query_mapping = resource2.QueryParameters(query_param=qp_name)
            base_path = "/%(something)s/blah"
            something = resource2.URI("something")

        results = list(Test.list(self.session, paginated=True,
                                 query_param=qp, something=uri_param))

        self.assertEqual(1, len(results))

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.session.get.call_args_list[0][1]["params"] = {qp_name: qp}

        self.assertEqual(self.session.get.call_args_list[0][0][0],
                         Test.base_path % {"something": uri_param})

    def test_list_multi_page_response_paginated(self):
        # This tests our ability to stop making calls once
        # we've received all of the data. However, this tests
        # the case that we always receive full pages of data
        # and then the signal that there is no more data - an empty list.
        # In this case, we need to make one extra request beyond
        # the end of data to ensure we've received it all.
        ids = [1, 2]
        resp1 = mock.Mock()
        resp1.json.return_value = [{"id": ids[0]}]
        resp2 = mock.Mock()
        resp2.json.return_value = [{"id": ids[1]}]
        resp3 = mock.Mock()
        resp3.json.return_value = []

        self.session.get.side_effect = [resp1, resp2, resp3]

        results = self.sot.list(self.session, paginated=True)

        result0 = next(results)
        self.assertEqual(result0.id, ids[0])
        self.session.get.assert_called_with(
            self.base_path,
            endpoint_filter=self.service_name,
            headers={"Accept": "application/json"},
            params={})

        result1 = next(results)
        self.assertEqual(result1.id, ids[1])
        self.session.get.assert_called_with(
            self.base_path,
            endpoint_filter=self.service_name,
            headers={"Accept": "application/json"},
            params={"limit": 1, "marker": 1})

        self.assertRaises(StopIteration, next, results)
        self.session.get.assert_called_with(
            self.base_path,
            endpoint_filter=self.service_name,
            headers={"Accept": "application/json"},
            params={"limit": 1, "marker": 2})

    def test_list_multi_page_early_termination(self):
        # This tests our ability to be somewhat smart when evaluating
        # the contents of the responses. When we receive a full page
        # of data, we can be smart about terminating our responses
        # once we see that we've received a page with less data than
        # expected, saving one request.
        ids = [1, 2, 3]
        resp1 = mock.Mock()
        resp1.json.return_value = [{"id": ids[0]}, {"id": ids[1]}]
        resp2 = mock.Mock()
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
            endpoint_filter=self.service_name,
            headers={"Accept": "application/json"},
            params={})

        # Second page only has one item
        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        self.session.get.assert_called_with(
            self.base_path,
            endpoint_filter=self.service_name,
            headers={"Accept": "application/json"},
            params={"limit": 2, "marker": 2})

        # Ensure we're done after those three items
        self.assertRaises(StopIteration, next, results)

        # Ensure we only made two calls to get this done
        self.assertEqual(2, len(self.session.get.call_args_list))


class TestResourceFind(base.TestCase):

    def setUp(self):
        super(TestResourceFind, self).setUp()

        self.result = 1

        class Base(resource2.Resource):

            @classmethod
            def existing(cls, **kwargs):
                raise exceptions.NotFoundException

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

        class Test(resource2.Resource):

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
        self.assertIsNone(resource2.Resource._get_one_match("name", []))

    def test_no_match_by_name(self):
        the_name = "Brian"

        match = mock.Mock(spec=resource2.Resource)
        match.name = the_name

        result = resource2.Resource._get_one_match("Richard", [match])

        self.assertIsNone(result, match)

    def test_single_match_by_name(self):
        the_name = "Brian"

        match = mock.Mock(spec=resource2.Resource)
        match.name = the_name

        result = resource2.Resource._get_one_match(the_name, [match])

        self.assertIs(result, match)

    def test_single_match_by_id(self):
        the_id = "Brian"

        match = mock.Mock(spec=resource2.Resource)
        match.id = the_id

        result = resource2.Resource._get_one_match(the_id, [match])

        self.assertIs(result, match)

    def test_single_match_by_alternate_id(self):
        the_id = "Richard"

        class Test(resource2.Resource):
            other_id = resource2.Body("other_id", alternate_id=True)

        match = Test(other_id=the_id)
        result = Test._get_one_match(the_id, [match])

        self.assertIs(result, match)

    def test_multiple_matches(self):
        the_id = "Brian"

        match = mock.Mock(spec=resource2.Resource)
        match.id = the_id

        self.assertRaises(
            exceptions.DuplicateResource,
            resource2.Resource._get_one_match, the_id, [match, match])


class TestWaitForStatus(base.TestCase):

    def test_immediate_status(self):
        status = "loling"
        resource = mock.Mock()
        resource.status = status

        result = resource2.wait_for_status("session", resource, status,
                                           "failures", "interval", "wait")

        self.assertEqual(result, resource)

    @mock.patch("time.sleep", return_value=None)
    def test_status_match(self, mock_sleep):
        status = "loling"
        resource = mock.Mock()

        # other gets past the first check, two anothers gets through
        # the sleep loop, and the third matches
        statuses = ["other", "another", "another", status]
        type(resource).status = mock.PropertyMock(side_effect=statuses)

        result = resource2.wait_for_status("session", resource, status,
                                           None, 1, 5)

        self.assertEqual(result, resource)

    @mock.patch("time.sleep", return_value=None)
    def test_status_fails(self, mock_sleep):
        status = "loling"
        failure = "crying"
        resource = mock.Mock()

        # other gets past the first check, the first failure doesn't
        # match the expected, the third matches the failure,
        # the fourth is used in creating the exception message
        statuses = ["other", failure, failure, failure]
        type(resource).status = mock.PropertyMock(side_effect=statuses)

        self.assertRaises(exceptions.ResourceFailure,
                          resource2.wait_for_status,
                          "session", resource, status, [failure], 1, 5)

    @mock.patch("time.sleep", return_value=None)
    def test_timeout(self, mock_sleep):
        status = "loling"
        resource = mock.Mock()

        # The first "other" gets past the first check, and then three
        # pairs of "other" statuses run through the sleep counter loop,
        # after which time should be up. This is because we have a
        # one second interval and three second waiting period.
        statuses = ["other"] * 7
        type(resource).status = mock.PropertyMock(side_effect=statuses)

        self.assertRaises(exceptions.ResourceTimeout,
                          resource2.wait_for_status,
                          "session", resource, status, None, 1, 3)

    def test_no_sleep(self):
        resource = mock.Mock()
        statuses = ["other"]
        type(resource).status = mock.PropertyMock(side_effect=statuses)

        self.assertRaises(exceptions.ResourceTimeout,
                          resource2.wait_for_status,
                          "session", resource, "status", None, 0, -1)


class TestWaitForDelete(base.TestCase):

    @mock.patch("time.sleep", return_value=None)
    def test_success(self, mock_sleep):
        resource = mock.Mock()
        resource.get.side_effect = [None, None, exceptions.NotFoundException]

        result = resource2.wait_for_delete("session", resource, 1, 3)

        self.assertEqual(result, resource)

    @mock.patch("time.sleep", return_value=None)
    def test_timeout(self, mock_sleep):
        resource = mock.Mock()
        resource.get.side_effect = [None, None, None]

        self.assertRaises(exceptions.ResourceTimeout,
                          resource2.wait_for_delete,
                          "session", resource, 1, 3)
