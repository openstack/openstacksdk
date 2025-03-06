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
import json
import logging
from unittest import mock

from keystoneauth1 import adapter
import requests

from openstack import dns
from openstack import exceptions
from openstack import fields
from openstack import resource
from openstack.tests.unit import base
from openstack import utils


class FakeResponse:
    def __init__(self, response, status_code=200, headers=None):
        self.body = response
        self.status_code = status_code
        headers = headers if headers else {'content-type': 'application/json'}
        self.headers = requests.structures.CaseInsensitiveDict(headers)

    def json(self):
        return self.body


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
        self.assertCountEqual(iter(attrs), sot.__iter__())

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
        mapping = {
            "first_name": "first-name",
            "second_name": {"name": "second-name"},
            "third_name": {"name": "third", "type": int},
        }

        sot = resource.QueryParameters(location, **mapping)

        self.assertEqual(
            {
                "location": "location",
                "first_name": "first-name",
                "second_name": {"name": "second-name"},
                "third_name": {"name": "third", "type": int},
                "limit": "limit",
                "marker": "marker",
            },
            sot._mapping,
        )

    def test_transpose_unmapped(self):
        def _type(value, rtype):
            self.assertIs(rtype, mock.sentinel.resource_type)
            return value * 10

        location = "location"
        mapping = {
            "first_name": "first-name",
            "pet_name": {"name": "pet"},
            "answer": {"name": "answer", "type": int},
            "complex": {"type": _type},
        }

        sot = resource.QueryParameters(location, **mapping)
        result = sot._transpose(
            {
                "location": "Brooklyn",
                "first_name": "Brian",
                "pet_name": "Meow",
                "answer": "42",
                "last_name": "Curtin",
                "complex": 1,
            },
            mock.sentinel.resource_type,
        )

        # last_name isn't mapped and shouldn't be included
        self.assertEqual(
            {
                "location": "Brooklyn",
                "first-name": "Brian",
                "pet": "Meow",
                "answer": 42,
                "complex": 10,
            },
            result,
        )

    def test_transpose_not_in_query(self):
        location = "location"
        mapping = {
            "first_name": "first-name",
            "pet_name": {"name": "pet"},
            "answer": {"name": "answer", "type": int},
        }

        sot = resource.QueryParameters(location, **mapping)
        result = sot._transpose(
            {"location": "Brooklyn"}, mock.sentinel.resource_type
        )

        # first_name not being in the query shouldn't affect results
        self.assertEqual({"location": "Brooklyn"}, result)


class TestResource(base.TestCase):
    def test_initialize_basic(self):
        body = {"body": 1}
        header = {"header": 2, "Location": "somewhere"}
        uri = {"uri": 3}
        computed = {"computed": 4}
        everything = dict(
            itertools.chain(
                body.items(),
                header.items(),
                uri.items(),
                computed.items(),
            )
        )

        mock_collect = mock.Mock()
        mock_collect.return_value = body, header, uri, computed

        with mock.patch.object(
            resource.Resource, "_collect_attrs", mock_collect
        ):
            sot = resource.Resource(_synchronized=False, **everything)
            mock_collect.assert_called_once_with(everything)
        self.assertIsNone(sot.location)

        self.assertIsInstance(sot._body, resource._ComponentManager)
        self.assertEqual(body, sot._body.dirty)
        self.assertIsInstance(sot._header, resource._ComponentManager)
        self.assertEqual(header, sot._header.dirty)
        self.assertIsInstance(sot._uri, resource._ComponentManager)
        self.assertEqual(uri, sot._uri.dirty)

        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_head)
        self.assertEqual('PUT', sot.commit_method)
        self.assertEqual('POST', sot.create_method)

    def test_repr(self):
        a = {"a": 1}
        b = {"b": 2}
        c = {"c": 3}
        d = {"d": 4}

        class Test(resource.Resource):
            def __init__(self):
                self._body = mock.Mock()
                self._body.attributes.items = mock.Mock(return_value=a.items())

                self._header = mock.Mock()
                self._header.attributes.items = mock.Mock(
                    return_value=b.items()
                )

                self._uri = mock.Mock()
                self._uri.attributes.items = mock.Mock(return_value=c.items())

                self._computed = mock.Mock()
                self._computed.attributes.items = mock.Mock(
                    return_value=d.items()
                )

        the_repr = repr(Test())

        # Don't test the arguments all together since the dictionary order
        # they're rendered in can't be depended on, nor does it matter.
        self.assertIn("openstack.tests.unit.test_resource.Test", the_repr)
        self.assertIn("a=1", the_repr)
        self.assertIn("b=2", the_repr)
        self.assertIn("c=3", the_repr)
        self.assertIn("d=4", the_repr)

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
        self.assertNotEqual(e1, None)

    def test__update(self):
        sot = resource.Resource()

        body = "body"
        header = "header"
        uri = "uri"
        computed = "computed"

        sot._collect_attrs = mock.Mock(
            return_value=(body, header, uri, computed)
        )
        sot._body.update = mock.Mock()
        sot._header.update = mock.Mock()
        sot._uri.update = mock.Mock()
        sot._computed.update = mock.Mock()

        args = {"arg": 1}
        sot._update(**args)

        sot._collect_attrs.assert_called_once_with(args)
        sot._body.update.assert_called_once_with(body)
        sot._header.update.assert_called_once_with(header)
        sot._uri.update.assert_called_once_with(uri)
        sot._computed.update.assert_called_with(computed)

    def test__consume_attrs(self):
        serverside_key1 = "someKey1"
        clientside_key1 = "some_key1"
        serverside_key2 = "someKey2"
        clientside_key2 = "some_key2"
        value1 = "value1"
        value2 = "value2"
        mapping = {
            serverside_key1: clientside_key1,
            serverside_key2: clientside_key2,
        }

        other_key = "otherKey"
        other_value = "other"
        attrs = {
            clientside_key1: value1,
            serverside_key2: value2,
            other_key: other_value,
        }

        sot = resource.Resource()

        result = sot._consume_attrs(mapping, attrs)

        # Make sure that the expected key was consumed and we're only
        # left with the other stuff.
        self.assertDictEqual({other_key: other_value}, attrs)

        # Make sure that after we've popped our relevant client-side
        # key off that we are returning it keyed off of its server-side
        # name.
        self.assertDictEqual(
            {serverside_key1: value1, serverside_key2: value2}, result
        )

    def test__mapping_defaults(self):
        # Check that even on an empty class, we get the expected
        # built-in attributes.

        self.assertIn("location", resource.Resource._computed_mapping())
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

        self.assertEqual("the_alt", Test._alternate_id())

        value1 = "lol"
        sot = Test(alt=value1)
        self.assertEqual(sot.alt, value1)
        self.assertEqual(sot.id, value1)

        value2 = "rofl"
        sot = Test(the_alt=value2)
        self.assertEqual(sot.alt, value2)
        self.assertEqual(sot.id, value2)

    def test__alternate_id_from_other_property(self):
        class Test(resource.Resource):
            foo = resource.Body("foo")
            bar = resource.Body("bar", alternate_id=True)

        # NOTE(redrobot): My expectation looking at the Test class defined
        # in this test is that because the alternate_id parameter is
        # is being set to True on the "bar" property of the Test class,
        # then the _alternate_id() method should return the name of that "bar"
        # property.
        self.assertEqual("bar", Test._alternate_id())
        sot = Test(bar='bunnies')
        self.assertEqual(sot.id, 'bunnies')
        self.assertEqual(sot.bar, 'bunnies')
        sot = Test(id='chickens', bar='bunnies')
        self.assertEqual(sot.id, 'chickens')
        self.assertEqual(sot.bar, 'bunnies')

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

    def test__attributes(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar', aka='_bar')
            bar_local = resource.Body('bar_remote')

        sot = Test()

        self.assertEqual(
            sorted(
                ['foo', 'bar', '_bar', 'bar_local', 'id', 'name', 'location']
            ),
            sorted(sot._attributes()),
        )

        self.assertEqual(
            sorted(['foo', 'bar', 'bar_local', 'id', 'name', 'location']),
            sorted(sot._attributes(include_aliases=False)),
        )

        self.assertEqual(
            sorted(
                ['foo', 'bar', '_bar', 'bar_remote', 'id', 'name', 'location']
            ),
            sorted(sot._attributes(remote_names=True)),
        )

        self.assertEqual(
            sorted(['bar', '_bar', 'bar_local', 'id', 'name', 'location']),
            sorted(sot._attributes(components=(fields.Body, fields.Computed))),
        )

        self.assertEqual(
            ('foo',),
            tuple(sot._attributes(components=(fields.Header,))),
        )

    def test__attributes_iterator(self):
        class Parent(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar', aka='_bar')

        class Child(Parent):
            foo1 = resource.Header('foo1')
            bar1 = resource.Body('bar1')

        sot = Child()
        expected = ['foo', 'bar', 'foo1', 'bar1']

        for attr, component in sot._attributes_iterator():
            if attr in expected:
                expected.remove(attr)
        self.assertEqual([], expected)

        expected = ['foo', 'foo1']

        # Check we iterate only over headers
        for attr, component in sot._attributes_iterator(
            components=(fields.Header,)
        ):
            if attr in expected:
                expected.remove(attr)
        self.assertEqual([], expected)

    def test_to_dict(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar', aka='_bar')

        res = Test(id='FAKE_ID')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'location': None,
            'foo': None,
            'bar': None,
            '_bar': None,
        }
        self.assertEqual(expected, res.to_dict())

    def test_to_dict_nested(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')
            a_list = resource.Body('a_list')

        class Sub(resource.Resource):
            sub = resource.Body('foo')

        sub = Sub(id='ANOTHER_ID', foo='bar')

        res = Test(id='FAKE_ID', bar=sub, a_list=[sub])

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'location': None,
            'foo': None,
            'bar': {
                'id': 'ANOTHER_ID',
                'name': None,
                'sub': 'bar',
                'location': None,
            },
            'a_list': [
                {
                    'id': 'ANOTHER_ID',
                    'name': None,
                    'sub': 'bar',
                    'location': None,
                }
            ],
        }
        self.assertEqual(expected, res.to_dict())
        a_munch = res.to_dict(_to_munch=True)
        self.assertEqual(a_munch.bar.id, 'ANOTHER_ID')
        self.assertEqual(a_munch.bar.sub, 'bar')
        self.assertEqual(a_munch.a_list[0].id, 'ANOTHER_ID')
        self.assertEqual(a_munch.a_list[0].sub, 'bar')

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
            'bar': None,
            'location': None,
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
            bar = resource.Body('bar', aka='_bar')

        class Child(Parent):
            foo_new = resource.Header('foo_baz_server')
            bar_new = resource.Body('bar_baz_server')

        res = Child(id='FAKE_ID', bar='test')

        expected = {
            'foo': None,
            'bar': 'test',
            '_bar': 'test',
            'foo_new': None,
            'bar_new': None,
            'id': 'FAKE_ID',
            'location': None,
            'name': None,
        }
        self.assertEqual(expected, res.to_dict())

    def test_to_dict_with_unknown_attrs_in_body(self):
        class Test(resource.Resource):
            foo = resource.Body('foo')
            _allow_unknown_attrs_in_body = True

        res = Test(id='FAKE_ID', foo='FOO', bar='BAR')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'location': None,
            'foo': 'FOO',
            'bar': 'BAR',
        }
        self.assertEqual(expected, res.to_dict())

    def test_json_dumps_from_resource(self):
        class Test(resource.Resource):
            foo = resource.Body('foo_remote')

        res = Test(foo='bar')

        expected = '{"foo": "bar", "id": null, "location": null, "name": null}'

        actual = json.dumps(res, sort_keys=True)
        self.assertEqual(expected, actual)

        response = FakeResponse({'foo': 'new_bar'})
        res._translate_response(response)

        expected = (
            '{"foo": "new_bar", "id": null, "location": null, "name": null}'
        )
        actual = json.dumps(res, sort_keys=True)
        self.assertEqual(expected, actual)

    def test_items(self):
        class Test(resource.Resource):
            foo = resource.Body('foo')
            bar = resource.Body('bar')
            foot = resource.Body('foot')

        data = {'foo': 'bar', 'bar': 'foo\n', 'foot': 'a:b:c:d'}

        res = Test(**data)
        for k, v in res.items():
            expected = data.get(k)
            if expected:
                self.assertEqual(v, expected)

    def test_access_by_aka(self):
        class Test(resource.Resource):
            foo = resource.Header('foo_remote', aka='foo_alias')

        res = Test(foo='bar', name='test')

        self.assertEqual('bar', res['foo_alias'])
        self.assertEqual('bar', res.foo_alias)
        self.assertTrue('foo' in res.keys())
        self.assertTrue('foo_alias' in res.keys())
        expected = utils.Munch(
            {
                'id': None,
                'name': 'test',
                'location': None,
                'foo': 'bar',
                'foo_alias': 'bar',
            }
        )
        actual = utils.Munch(res)
        self.assertEqual(expected, actual)
        self.assertEqual(expected, res.toDict())
        self.assertEqual(expected, res.to_dict())
        self.assertDictEqual(expected, res)
        self.assertDictEqual(expected, dict(res))

    def test_access_by_resource_name(self):
        class Test(resource.Resource):
            blah = resource.Body("blah_resource")

        sot = Test(blah='dummy')

        result = sot["blah_resource"]
        self.assertEqual(result, sot.blah)

    def test_to_dict_value_error(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        err = self.assertRaises(
            ValueError, res.to_dict, body=False, headers=False, computed=False
        )
        self.assertEqual(
            'At least one of `body`, `headers` or `computed` must be True',
            str(err),
        )

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
            'name': None,
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

    def test_from_munch_new(self):
        class Test(resource.Resource):
            attr = resource.Body("body_attr")

        value = "value"
        orig = utils.Munch(body_attr=value)
        sot = Test._from_munch(orig, synchronized=False)

        self.assertIn("body_attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test_from_munch_existing(self):
        class Test(resource.Resource):
            attr = resource.Body("body_attr")

        value = "value"
        orig = utils.Munch(body_attr=value)
        sot = Test._from_munch(orig)

        self.assertNotIn("body_attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test__prepare_request_with_id(self):
        class Test(resource.Resource):
            base_path = "/something"
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        the_id = "id"
        body_value = "body"
        header_value = "header"
        sot = Test(
            id=the_id,
            body_attr=body_value,
            header_attr=header_value,
            _synchronized=False,
        )

        result = sot._prepare_request(requires_id=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual({"x": body_value, "id": the_id}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_with_id_marked_clean(self):
        class Test(resource.Resource):
            base_path = "/something"
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        the_id = "id"
        body_value = "body"
        header_value = "header"
        sot = Test(
            id=the_id,
            body_attr=body_value,
            header_attr=header_value,
            _synchronized=False,
        )
        sot._body._dirty.discard("id")

        result = sot._prepare_request(requires_id=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual({"x": body_value}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_missing_id(self):
        sot = resource.Resource(id=None)

        self.assertRaises(
            exceptions.InvalidRequest, sot._prepare_request, requires_id=True
        )

    def test__prepare_request_with_resource_key(self):
        key = "key"

        class Test(resource.Resource):
            base_path = "/something"
            resource_key = key
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        body_value = "body"
        header_value = "header"
        sot = Test(
            body_attr=body_value, header_attr=header_value, _synchronized=False
        )

        result = sot._prepare_request(requires_id=False, prepend_key=True)

        self.assertEqual("/something", result.url)
        self.assertEqual({key: {"x": body_value}}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_with_override_key(self):
        default_key = "key"
        override_key = "other_key"

        class Test(resource.Resource):
            base_path = "/something"
            resource_key = default_key
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        body_value = "body"
        header_value = "header"
        sot = Test(
            body_attr=body_value, header_attr=header_value, _synchronized=False
        )

        result = sot._prepare_request(
            requires_id=False,
            prepend_key=True,
            resource_request_key=override_key,
        )

        self.assertEqual("/something", result.url)
        self.assertEqual({override_key: {"x": body_value}}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_with_patch(self):
        class Test(resource.Resource):
            commit_jsonpatch = True
            base_path = "/something"
            x = resource.Body("x")
            y = resource.Body("y")

        the_id = "id"
        sot = Test.existing(id=the_id, x=1, y=2)
        sot.x = 3

        result = sot._prepare_request(requires_id=True, patch=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual(
            [{'op': 'replace', 'path': '/x', 'value': 3}], result.body
        )

    def test__prepare_request_with_patch_not_synchronized(self):
        class Test(resource.Resource):
            commit_jsonpatch = True
            base_path = "/something"
            x = resource.Body("x")
            y = resource.Body("y")

        the_id = "id"
        sot = Test.new(id=the_id, x=1)

        result = sot._prepare_request(requires_id=True, patch=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual(
            [{'op': 'add', 'path': '/x', 'value': 1}], result.body
        )

    def test__prepare_request_with_patch_params(self):
        class Test(resource.Resource):
            commit_jsonpatch = True
            base_path = "/something"
            x = resource.Body("x")
            y = resource.Body("y")

        the_id = "id"
        sot = Test.existing(id=the_id, x=1, y=2)
        sot.x = 3

        params = [('foo', 'bar'), ('life', 42)]

        result = sot._prepare_request(
            requires_id=True, patch=True, params=params
        )

        self.assertEqual("something/id?foo=bar&life=42", result.url)
        self.assertEqual(
            [{'op': 'replace', 'path': '/x', 'value': 3}], result.body
        )

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
            allow_fetch = False
            allow_commit = False
            allow_delete = False
            allow_head = False
            allow_list = False

        sot = Test()

        # The first argument to all of these operations is the session,
        # but we raise before we get to it so just pass anything in.
        self.assertRaises(exceptions.MethodNotSupported, sot.create, "")
        self.assertRaises(exceptions.MethodNotSupported, sot.fetch, "")
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
        self.assertRaises(exceptions.MethodNotSupported, sot.commit, "")

    def test_unknown_attrs_under_props_create(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )
        self.assertDictEqual({'dummy': 'value'}, sot.properties)
        self.assertDictEqual({'dummy': 'value'}, sot.to_dict()['properties'])
        self.assertDictEqual({'dummy': 'value'}, sot['properties'])
        self.assertEqual('value', sot['properties']['dummy'])

        sot = Test.new(**{'dummy': 'value', 'properties': 'a,b,c'})
        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'}, sot.properties
        )
        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'},
            sot.to_dict()['properties'],
        )

        sot = Test.new(**{'properties': None})
        self.assertIsNone(sot.properties)
        self.assertIsNone(sot.to_dict()['properties'])

    def test_unknown_attrs_not_stored(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )
        self.assertIsNone(sot.properties)

    def test_unknown_attrs_not_stored1(self):
        class Test(resource.Resource):
            _store_unknown_attrs_as_properties = True

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )
        self.assertRaises(KeyError, sot.__getitem__, 'properties')

    def test_unknown_attrs_under_props_set(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )

        sot['properties'] = {'dummy': 'new_value'}
        self.assertEqual('new_value', sot['properties']['dummy'])
        sot.properties = {'dummy': 'new_value1'}
        self.assertEqual('new_value1', sot['properties']['dummy'])

    def test_unknown_attrs_prepare_request_unpacked(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        # Unknown attribute given as root attribute
        sot = Test.new(**{'dummy': 'value', 'properties': 'a,b,c'})

        request_body = sot._prepare_request(requires_id=False).body
        self.assertEqual('value', request_body['dummy'])
        self.assertEqual('a,b,c', request_body['properties'])

        # properties are already a dict
        sot = Test.new(
            **{'properties': {'properties': 'a,b,c', 'dummy': 'value'}}
        )

        request_body = sot._prepare_request(requires_id=False).body
        self.assertEqual('value', request_body['dummy'])
        self.assertEqual('a,b,c', request_body['properties'])

    def test_unknown_attrs_prepare_request_no_unpack_dict(self):
        # if props type is not None - ensure no unpacking is done
        class Test(resource.Resource):
            properties = resource.Body("properties", type=dict)

        sot = Test.new(
            **{'properties': {'properties': 'a,b,c', 'dummy': 'value'}}
        )

        request_body = sot._prepare_request(requires_id=False).body
        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'},
            request_body['properties'],
        )

    def test_unknown_attrs_prepare_request_patch_unpacked(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True
            commit_jsonpatch = True

        sot = Test.existing(**{'dummy': 'value', 'properties': 'a,b,c'})

        sot._update(**{'properties': {'dummy': 'new_value'}})

        request_body = sot._prepare_request(requires_id=False, patch=True).body
        self.assertDictEqual(
            {'path': '/dummy', 'value': 'new_value', 'op': 'replace'},
            request_body[0],
        )

    def test_unknown_attrs_under_props_translate_response(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        body = {'dummy': 'value', 'properties': 'a,b,c'}
        response = FakeResponse(body)

        sot = Test()

        sot._translate_response(response, has_body=True)

        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'}, sot.properties
        )

    def test_unknown_attrs_in_body_create(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = True

        sot = Test.new(**{'known_param': 'v1', 'unknown_param': 'v2'})
        self.assertEqual('v1', sot.known_param)
        self.assertEqual('v2', sot.unknown_param)

    def test_unknown_attrs_in_body_not_stored(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            properties = resource.Body("properties")

        sot = Test.new(**{'known_param': 'v1', 'unknown_param': 'v2'})
        self.assertEqual('v1', sot.known_param)
        self.assertNotIn('unknown_param', sot)

    def test_unknown_attrs_in_body_set(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = True

        sot = Test.new(
            **{
                'known_param': 'v1',
            }
        )
        sot['unknown_param'] = 'v2'

        self.assertEqual('v1', sot.known_param)
        self.assertEqual('v2', sot.unknown_param)

    def test_unknown_attrs_in_body_not_allowed_to_set(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = False

        sot = Test.new(
            **{
                'known_param': 'v1',
            }
        )
        try:
            sot['unknown_param'] = 'v2'
        except KeyError:
            self.assertEqual('v1', sot.known_param)
            self.assertNotIn('unknown_param', sot)
            return
        self.fail(
            "Parameter 'unknown_param' unexpectedly set through the "
            "dict interface"
        )

    def test_unknown_attrs_in_body_translate_response(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = True

        body = {'known_param': 'v1', 'unknown_param': 'v2'}
        response = FakeResponse(body)

        sot = Test()
        sot._translate_response(response, has_body=True)

        self.assertEqual('v1', sot.known_param)
        self.assertEqual('v2', sot.unknown_param)

    def test_unknown_attrs_not_in_body_translate_response(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = False

        body = {'known_param': 'v1', 'unknown_param': 'v2'}
        response = FakeResponse(body)

        sot = Test()
        sot._translate_response(response, has_body=True)

        self.assertEqual('v1', sot.known_param)
        self.assertNotIn('unknown_param', sot)


class TestResourceActions(base.TestCase):
    def setUp(self):
        super().setUp()

        self.service_name = "service"
        self.base_path = "base_path"

        class Test(resource.Resource):
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
        self.session.session = self.session
        self.session._get_connection = mock.Mock(return_value=self.cloud)
        self.session.default_microversion = None
        self.session.retriable_status_codes = None

        self.endpoint_data = mock.Mock(
            max_microversion='1.99', min_microversion=None
        )
        self.session.get_endpoint_data.return_value = self.endpoint_data

    def _test_create(
        self,
        cls,
        requires_id=False,
        prepend_key=False,
        microversion=None,
        base_path=None,
        params=None,
        id_marked_dirty=True,
        explicit_microversion=None,
        resource_request_key=None,
        resource_response_key=None,
    ):
        id = "id" if requires_id else None
        sot = cls(id=id)
        sot._prepare_request = mock.Mock(return_value=self.request)
        sot._translate_response = mock.Mock()

        params = params or {}
        kwargs = params.copy()
        if explicit_microversion is not None:
            kwargs['microversion'] = explicit_microversion
            microversion = explicit_microversion
        result = sot.create(
            self.session,
            prepend_key=prepend_key,
            base_path=base_path,
            resource_request_key=resource_request_key,
            resource_response_key=resource_response_key,
            **kwargs,
        )

        id_is_dirty = 'id' in sot._body._dirty
        self.assertEqual(id_marked_dirty, id_is_dirty)
        prepare_kwargs = {}
        if resource_request_key is not None:
            prepare_kwargs['resource_request_key'] = resource_request_key

        sot._prepare_request.assert_called_once_with(
            requires_id=requires_id,
            prepend_key=prepend_key,
            base_path=base_path,
            **prepare_kwargs,
        )
        if requires_id:
            self.session.put.assert_called_once_with(
                self.request.url,
                json=self.request.body,
                headers=self.request.headers,
                microversion=microversion,
                params=params,
            )
        else:
            self.session.post.assert_called_once_with(
                self.request.url,
                json=self.request.body,
                headers=self.request.headers,
                microversion=microversion,
                params=params,
            )

        self.assertEqual(sot.microversion, microversion)
        sot._translate_response.assert_called_once_with(
            self.response,
            has_body=sot.has_body,
            resource_response_key=resource_response_key,
        )
        self.assertEqual(result, sot)

    def test_put_create(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'PUT'

        self._test_create(Test, requires_id=True, prepend_key=True)

    def test_put_create_exclude_id(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'PUT'
            create_exclude_id_from_body = True

        self._test_create(
            Test, requires_id=True, prepend_key=True, id_marked_dirty=False
        )

    def test_put_create_with_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'PUT'
            _max_microversion = '1.42'

        self._test_create(
            Test, requires_id=True, prepend_key=True, microversion='1.42'
        )

    def test_put_create_with_explicit_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'PUT'
            _max_microversion = '1.99'

        self._test_create(
            Test,
            requires_id=True,
            prepend_key=True,
            explicit_microversion='1.42',
        )

    def test_put_create_with_params(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'PUT'

        self._test_create(
            Test, requires_id=True, prepend_key=True, params={'answer': 42}
        )

    def test_post_create(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'POST'

        self._test_create(Test, requires_id=False, prepend_key=True)

    def test_post_create_override_request_key(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'POST'
            resource_key = 'SomeKey'

        self._test_create(
            Test,
            requires_id=False,
            prepend_key=True,
            resource_request_key="OtherKey",
        )

    def test_post_create_override_response_key(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'POST'
            resource_key = 'SomeKey'

        self._test_create(
            Test,
            requires_id=False,
            prepend_key=True,
            resource_response_key="OtherKey",
        )

    def test_post_create_override_key_both(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'POST'
            resource_key = 'SomeKey'

        self._test_create(
            Test,
            requires_id=False,
            prepend_key=True,
            resource_request_key="OtherKey",
            resource_response_key="SomeOtherKey",
        )

    def test_post_create_base_path(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'POST'

        self._test_create(
            Test, requires_id=False, prepend_key=True, base_path='dummy'
        )

    def test_post_create_with_params(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_create = True
            create_method = 'POST'

        self._test_create(
            Test, requires_id=False, prepend_key=True, params={'answer': 42}
        )

    def test_fetch(self):
        result = self.sot.fetch(self.session)

        self.sot._prepare_request.assert_called_once_with(
            requires_id=True, base_path=None
        )
        self.session.get.assert_called_once_with(
            self.request.url, microversion=None, params={}, skip_cache=False
        )

        self.assertIsNone(self.sot.microversion)
        self.sot._translate_response.assert_called_once_with(
            self.response, error_message=None, resource_response_key=None
        )
        self.assertEqual(result, self.sot)

    def test_fetch_with_override_key(self):
        result = self.sot.fetch(self.session, resource_response_key="SomeKey")

        self.sot._prepare_request.assert_called_once_with(
            requires_id=True, base_path=None
        )
        self.session.get.assert_called_once_with(
            self.request.url, microversion=None, params={}, skip_cache=False
        )

        self.assertIsNone(self.sot.microversion)
        self.sot._translate_response.assert_called_once_with(
            self.response, error_message=None, resource_response_key="SomeKey"
        )
        self.assertEqual(result, self.sot)

    def test_fetch_with_params(self):
        result = self.sot.fetch(self.session, fields='a,b')

        self.sot._prepare_request.assert_called_once_with(
            requires_id=True, base_path=None
        )
        self.session.get.assert_called_once_with(
            self.request.url,
            microversion=None,
            params={'fields': 'a,b'},
            skip_cache=False,
        )

        self.assertIsNone(self.sot.microversion)
        self.sot._translate_response.assert_called_once_with(
            self.response, error_message=None, resource_response_key=None
        )
        self.assertEqual(result, self.sot)

    def test_fetch_with_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_fetch = True
            _max_microversion = '1.42'

        sot = Test(id='id')
        sot._prepare_request = mock.Mock(return_value=self.request)
        sot._translate_response = mock.Mock()

        result = sot.fetch(self.session)

        sot._prepare_request.assert_called_once_with(
            requires_id=True, base_path=None
        )
        self.session.get.assert_called_once_with(
            self.request.url, microversion='1.42', params={}, skip_cache=False
        )

        self.assertEqual(sot.microversion, '1.42')
        sot._translate_response.assert_called_once_with(
            self.response, error_message=None, resource_response_key=None
        )
        self.assertEqual(result, sot)

    def test_fetch_with_explicit_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_fetch = True
            _max_microversion = '1.99'

        sot = Test(id='id')
        sot._prepare_request = mock.Mock(return_value=self.request)
        sot._translate_response = mock.Mock()

        result = sot.fetch(self.session, microversion='1.42')

        sot._prepare_request.assert_called_once_with(
            requires_id=True, base_path=None
        )
        self.session.get.assert_called_once_with(
            self.request.url, microversion='1.42', params={}, skip_cache=False
        )

        self.assertEqual(sot.microversion, '1.42')
        sot._translate_response.assert_called_once_with(
            self.response, error_message=None, resource_response_key=None
        )
        self.assertEqual(result, sot)

    def test_fetch_not_requires_id(self):
        result = self.sot.fetch(self.session, False)

        self.sot._prepare_request.assert_called_once_with(
            requires_id=False, base_path=None
        )
        self.session.get.assert_called_once_with(
            self.request.url, microversion=None, params={}, skip_cache=False
        )

        self.sot._translate_response.assert_called_once_with(
            self.response, error_message=None, resource_response_key=None
        )
        self.assertEqual(result, self.sot)

    def test_fetch_base_path(self):
        result = self.sot.fetch(self.session, False, base_path='dummy')

        self.sot._prepare_request.assert_called_once_with(
            requires_id=False, base_path='dummy'
        )
        self.session.get.assert_called_once_with(
            self.request.url, microversion=None, params={}, skip_cache=False
        )

        self.sot._translate_response.assert_called_once_with(
            self.response, error_message=None, resource_response_key=None
        )
        self.assertEqual(result, self.sot)

    def test_head(self):
        result = self.sot.head(self.session)

        self.sot._prepare_request.assert_called_once_with(base_path=None)
        self.session.head.assert_called_once_with(
            self.request.url, microversion=None
        )

        self.assertIsNone(self.sot.microversion)
        self.sot._translate_response.assert_called_once_with(
            self.response,
            has_body=False,
        )
        self.assertEqual(result, self.sot)

    def test_head_base_path(self):
        result = self.sot.head(self.session, base_path='dummy')

        self.sot._prepare_request.assert_called_once_with(base_path='dummy')
        self.session.head.assert_called_once_with(
            self.request.url, microversion=None
        )

        self.assertIsNone(self.sot.microversion)
        self.sot._translate_response.assert_called_once_with(
            self.response,
            has_body=False,
        )
        self.assertEqual(result, self.sot)

    def test_head_with_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_head = True
            _max_microversion = '1.42'

        sot = Test(id='id')
        sot._prepare_request = mock.Mock(return_value=self.request)
        sot._translate_response = mock.Mock()

        result = sot.head(self.session)

        sot._prepare_request.assert_called_once_with(base_path=None)
        self.session.head.assert_called_once_with(
            self.request.url, microversion='1.42'
        )

        self.assertEqual(sot.microversion, '1.42')
        sot._translate_response.assert_called_once_with(
            self.response,
            has_body=False,
        )
        self.assertEqual(result, sot)

    def _test_commit(
        self,
        commit_method='PUT',
        prepend_key=True,
        has_body=True,
        microversion=None,
        commit_args=None,
        expected_args=None,
        base_path=None,
        explicit_microversion=None,
    ):
        self.sot.commit_method = commit_method

        # Need to make sot look dirty so we can attempt an update
        self.sot._body = mock.Mock()
        self.sot._body.dirty = mock.Mock(return_value={"x": "y"})

        commit_args = commit_args or {}
        if explicit_microversion is not None:
            commit_args['microversion'] = explicit_microversion
            microversion = explicit_microversion
        self.sot.commit(
            self.session,
            prepend_key=prepend_key,
            has_body=has_body,
            base_path=base_path,
            **commit_args,
        )

        self.sot._prepare_request.assert_called_once_with(
            prepend_key=prepend_key, base_path=base_path
        )

        if commit_method == 'PATCH':
            self.session.patch.assert_called_once_with(
                self.request.url,
                json=self.request.body,
                headers=self.request.headers,
                microversion=microversion,
                **(expected_args or {}),
            )
        elif commit_method == 'POST':
            self.session.post.assert_called_once_with(
                self.request.url,
                json=self.request.body,
                headers=self.request.headers,
                microversion=microversion,
                **(expected_args or {}),
            )
        elif commit_method == 'PUT':
            self.session.put.assert_called_once_with(
                self.request.url,
                json=self.request.body,
                headers=self.request.headers,
                microversion=microversion,
                **(expected_args or {}),
            )

        self.assertEqual(self.sot.microversion, microversion)
        self.sot._translate_response.assert_called_once_with(
            self.response,
            has_body=has_body,
        )

    def test_commit_put(self):
        self._test_commit(commit_method='PUT', prepend_key=True, has_body=True)

    def test_commit_patch(self):
        self._test_commit(
            commit_method='PATCH', prepend_key=False, has_body=False
        )

    def test_commit_base_path(self):
        self._test_commit(
            commit_method='PUT',
            prepend_key=True,
            has_body=True,
            base_path='dummy',
        )

    def test_commit_patch_retry_on_conflict(self):
        self._test_commit(
            commit_method='PATCH',
            commit_args={'retry_on_conflict': True},
            expected_args={'retriable_status_codes': {409}},
        )

    def test_commit_put_retry_on_conflict(self):
        self._test_commit(
            commit_method='PUT',
            commit_args={'retry_on_conflict': True},
            expected_args={'retriable_status_codes': {409}},
        )

    def test_commit_patch_no_retry_on_conflict(self):
        self.session.retriable_status_codes = {409, 503}
        self._test_commit(
            commit_method='PATCH',
            commit_args={'retry_on_conflict': False},
            expected_args={'retriable_status_codes': {503}},
        )

    def test_commit_put_no_retry_on_conflict(self):
        self.session.retriable_status_codes = {409, 503}
        self._test_commit(
            commit_method='PATCH',
            commit_args={'retry_on_conflict': False},
            expected_args={'retriable_status_codes': {503}},
        )

    def test_commit_put_explicit_microversion(self):
        self._test_commit(
            commit_method='PUT',
            prepend_key=True,
            has_body=True,
            explicit_microversion='1.42',
        )

    def test_commit_not_dirty(self):
        self.sot._body = mock.Mock()
        self.sot._body.dirty = dict()
        self.sot._header = mock.Mock()
        self.sot._header.dirty = dict()

        self.sot.commit(self.session)

        self.session.put.assert_not_called()

    def test_patch_with_sdk_names(self):
        class Test(resource.Resource):
            allow_patch = True

            id = resource.Body('id')
            attr = resource.Body('attr')
            nested = resource.Body('renamed')
            other = resource.Body('other')

        test_patch = [
            {'path': '/attr', 'op': 'replace', 'value': 'new'},
            {'path': '/nested/dog', 'op': 'remove'},
            {'path': '/nested/cat', 'op': 'add', 'value': 'meow'},
        ]
        expected = [
            {'path': '/attr', 'op': 'replace', 'value': 'new'},
            {'path': '/renamed/dog', 'op': 'remove'},
            {'path': '/renamed/cat', 'op': 'add', 'value': 'meow'},
        ]
        sot = Test.existing(id=1, attr=42, nested={'dog': 'bark'})
        sot.patch(self.session, test_patch)
        self.session.patch.assert_called_once_with(
            '/1', json=expected, headers=mock.ANY, microversion=None
        )

    def test_patch_with_server_names(self):
        class Test(resource.Resource):
            allow_patch = True

            id = resource.Body('id')
            attr = resource.Body('attr')
            nested = resource.Body('renamed')
            other = resource.Body('other')

        test_patch = [
            {'path': '/attr', 'op': 'replace', 'value': 'new'},
            {'path': '/renamed/dog', 'op': 'remove'},
            {'path': '/renamed/cat', 'op': 'add', 'value': 'meow'},
        ]
        sot = Test.existing(id=1, attr=42, nested={'dog': 'bark'})
        sot.patch(self.session, test_patch)
        self.session.patch.assert_called_once_with(
            '/1', json=test_patch, headers=mock.ANY, microversion=None
        )

    def test_patch_with_changed_fields(self):
        class Test(resource.Resource):
            allow_patch = True

            attr = resource.Body('attr')
            nested = resource.Body('renamed')
            other = resource.Body('other')

        sot = Test.existing(id=1, attr=42, nested={'dog': 'bark'})
        sot.attr = 'new'
        sot.patch(self.session, {'path': '/renamed/dog', 'op': 'remove'})

        expected = [
            {'path': '/attr', 'op': 'replace', 'value': 'new'},
            {'path': '/renamed/dog', 'op': 'remove'},
        ]
        self.session.patch.assert_called_once_with(
            '/1', json=expected, headers=mock.ANY, microversion=None
        )

    def test_delete(self):
        result = self.sot.delete(self.session)

        self.sot._prepare_request.assert_called_once_with()
        self.session.delete.assert_called_once_with(
            self.request.url, headers='headers', microversion=None
        )

        self.sot._translate_response.assert_called_once_with(
            self.response,
            has_body=False,
            error_message=None,
        )
        self.assertEqual(result, self.sot)

    def test_delete_with_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_delete = True
            _max_microversion = '1.42'

        sot = Test(id='id')
        sot._prepare_request = mock.Mock(return_value=self.request)
        sot._translate_response = mock.Mock()

        result = sot.delete(self.session)

        sot._prepare_request.assert_called_once_with()
        self.session.delete.assert_called_once_with(
            self.request.url, headers='headers', microversion='1.42'
        )

        sot._translate_response.assert_called_once_with(
            self.response,
            has_body=False,
            error_message=None,
        )
        self.assertEqual(result, sot)

    def test_delete_with_explicit_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            allow_delete = True
            _max_microversion = '1.99'

        sot = Test(id='id')
        sot._prepare_request = mock.Mock(return_value=self.request)
        sot._translate_response = mock.Mock()

        result = sot.delete(self.session, microversion='1.42')

        sot._prepare_request.assert_called_once_with()
        self.session.delete.assert_called_once_with(
            self.request.url, headers='headers', microversion='1.42'
        )

        sot._translate_response.assert_called_once_with(
            self.response, has_body=False, error_message=None
        )
        self.assertEqual(result, sot)

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
            params={},
            microversion=None,
        )

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
            params={},
            microversion=None,
        )

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
        mock_response.links = []

        self.session.get.return_value = mock_response

        sot = Test()

        results = list(sot.list(self.session))

        self.session.get.assert_called_once_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={},
            microversion=None,
        )

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
            "resources_links": [
                {
                    "href": "https://example.com/next-url",
                    "rel": "next",
                }
            ],
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
            mock.call(
                'base_path',
                headers={'Accept': 'application/json'},
                params={},
                microversion=None,
            ),
            self.session.get.mock_calls[0],
        )
        self.assertEqual(
            mock.call(
                'https://example.com/next-url',
                headers={'Accept': 'application/json'},
                params={},
                microversion=None,
            ),
            self.session.get.mock_calls[1],
        )
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
                "resources_links": [
                    {
                        "href": "https://example.com/next-url",
                        "rel": "next",
                    }
                ],
            },
            {
                "resources": [{"id": ids[1]}],
            },
        ]

        self.session.get.return_value = mock_response

        results = list(self.sot.list(self.session, paginated=True))

        self.assertEqual(2, len(results))
        self.assertEqual(ids[0], results[0].id)
        self.assertEqual(ids[1], results[1].id)
        self.assertEqual(
            mock.call(
                'base_path',
                headers={'Accept': 'application/json'},
                params={},
                microversion=None,
            ),
            self.session.get.mock_calls[0],
        )
        self.assertEqual(
            mock.call(
                'https://example.com/next-url',
                headers={'Accept': 'application/json'},
                params={},
                microversion=None,
            ),
            self.session.get.mock_calls[2],
        )
        self.assertEqual(2, len(self.session.get.call_args_list))
        self.assertIsInstance(results[0], self.test_class)

    def test_list_response_paginated_with_links_and_query(self):
        q_limit = 1
        ids = [1, 2]
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.side_effect = [
            {
                "resources": [{"id": ids[0]}],
                "resources_links": [
                    {
                        "href": f"https://example.com/next-url?limit={q_limit}",
                        "rel": "next",
                    }
                ],
            },
            {
                "resources": [{"id": ids[1]}],
            },
            {
                "resources": [],
            },
        ]

        self.session.get.return_value = mock_response

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters("limit")

        results = list(Test.list(self.session, paginated=True, limit=q_limit))

        self.assertEqual(2, len(results))
        self.assertEqual(ids[0], results[0].id)
        self.assertEqual(ids[1], results[1].id)
        self.assertEqual(
            mock.call(
                'base_path',
                headers={'Accept': 'application/json'},
                params={
                    'limit': q_limit,
                },
                microversion=None,
            ),
            self.session.get.mock_calls[0],
        )
        self.assertEqual(
            mock.call(
                'https://example.com/next-url',
                headers={'Accept': 'application/json'},
                params={
                    'limit': [str(q_limit)],
                },
                microversion=None,
            ),
            self.session.get.mock_calls[2],
        )

        self.assertEqual(3, len(self.session.get.call_args_list))
        self.assertIsInstance(results[0], self.test_class)

    def test_list_response_paginated_with_next_field(self):
        """Test pagination with a 'next' field in the response.

        Glance doesn't return a 'links' field in the response. Instead, it
        returns a 'first' field and, if there are more pages, a 'next' field in
        the response body. Ensure we correctly parse these.
        """

        class Test(resource.Resource):
            service = self.service_name
            base_path = '/foos/bars'
            resources_key = 'bars'
            allow_list = True
            _query_mapping = resource.QueryParameters("wow")

        ids = [1, 2]
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.side_effect = [
            {
                "bars": [{"id": ids[0]}],
                "first": "/v2/foos/bars?wow=cool",
                "next": "/v2/foos/bars?marker=baz&wow=cool",
            },
            {
                "bars": [{"id": ids[1]}],
                "first": "/v2/foos/bars?wow=cool",
            },
        ]

        self.session.get.return_value = mock_response

        results = list(Test.list(self.session, paginated=True, wow="cool"))

        self.assertEqual(2, len(results))
        self.assertEqual(ids[0], results[0].id)
        self.assertEqual(ids[1], results[1].id)
        self.assertEqual(
            mock.call(
                Test.base_path,
                headers={'Accept': 'application/json'},
                params={'wow': 'cool'},
                microversion=None,
            ),
            self.session.get.mock_calls[0],
        )
        self.assertEqual(
            mock.call(
                '/foos/bars',
                headers={'Accept': 'application/json'},
                params={'wow': ['cool'], 'marker': ['baz']},
                microversion=None,
            ),
            self.session.get.mock_calls[2],
        )

        self.assertEqual(2, len(self.session.get.call_args_list))
        self.assertIsInstance(results[0], Test)

    def test_list_response_paginated_with_microversions(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            resources_key = 'resources'
            allow_list = True
            _max_microversion = '1.42'

        ids = [1, 2]
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = {
            "resources": [{"id": ids[0]}],
            "resources_links": [
                {
                    "href": "https://example.com/next-url",
                    "rel": "next",
                }
            ],
        }
        mock_response2 = mock.Mock()
        mock_response2.status_code = 200
        mock_response2.links = {}
        mock_response2.json.return_value = {
            "resources": [{"id": ids[1]}],
        }

        self.session.get.side_effect = [mock_response, mock_response2]

        results = list(Test.list(self.session, paginated=True))

        self.assertEqual(2, len(results))
        self.assertEqual(ids[0], results[0].id)
        self.assertEqual(ids[1], results[1].id)
        self.assertEqual(
            mock.call(
                'base_path',
                headers={'Accept': 'application/json'},
                params={},
                microversion='1.42',
            ),
            self.session.get.mock_calls[0],
        )
        self.assertEqual(
            mock.call(
                'https://example.com/next-url',
                headers={'Accept': 'application/json'},
                params={},
                microversion='1.42',
            ),
            self.session.get.mock_calls[1],
        )
        self.assertEqual(2, len(self.session.get.call_args_list))
        self.assertIsInstance(results[0], Test)
        self.assertEqual('1.42', results[0].microversion)

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

    def test_list_paginated_infinite_loop(self):
        q_limit = 1
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.side_effect = [
            {
                "resources": [{"id": 1}],
            },
            {
                "resources": [{"id": 1}],
            },
        ]

        self.session.get.return_value = mock_response

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters("limit")

        res = Test.list(self.session, paginated=True, limit=q_limit)

        self.assertRaises(exceptions.SDKException, list, res)

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

        results = list(
            Test.list(
                self.session,
                paginated=True,
                query_param=qp,
                something=uri_param,
            )
        )

        self.assertEqual(1, len(results))
        # Verify URI attribute is set on the resource
        self.assertEqual(results[0].something, uri_param)

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.assertEqual(
            self.session.get.call_args_list[0][1]["params"], {qp_name: qp}
        )

        self.assertEqual(
            self.session.get.call_args_list[0][0][0],
            Test.base_path % {"something": uri_param},
        )

    def test_list_with_injected_headers(self):
        mock_empty = mock.Mock()
        mock_empty.status_code = 200
        mock_empty.json.return_value = {"resources": []}

        self.session.get.side_effect = [mock_empty]

        _ = list(
            self.test_class.list(self.session, headers={'X-Test': 'value'})
        )

        expected = {'Accept': 'application/json', 'X-Test': 'value'}
        self.assertEqual(
            expected, self.session.get.call_args.kwargs['headers']
        )

    @mock.patch.object(resource.Resource, 'list')
    def test_list_dns_with_headers(self, mock_resource_list):
        dns.v2._base.Resource.list(
            self.session,
            project_id='1234',
            all_projects=True,
        )

        expected = {
            'x-auth-sudo-project-id': '1234',
            'x-auth-all-projects': 'True',
        }
        self.assertEqual(
            expected, mock_resource_list.call_args.kwargs['headers']
        )

    def test_allow_invalid_list_params(self):
        qp = "query param!"
        qp_name = "query-param"
        uri_param = "uri param!"

        mock_empty = mock.Mock()
        mock_empty.status_code = 200
        mock_empty.links = {}
        mock_empty.json.return_value = {"resources": []}

        self.session.get.side_effect = [mock_empty]

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters(query_param=qp_name)
            base_path = "/%(something)s/blah"
            something = resource.URI("something")

        list(
            Test.list(
                self.session,
                paginated=True,
                query_param=qp,
                allow_unknown_params=True,
                something=uri_param,
                something_wrong=True,
            )
        )
        self.session.get.assert_called_once_with(
            f"/{uri_param}/blah",
            headers={'Accept': 'application/json'},
            microversion=None,
            params={qp_name: qp},
        )

    def test_list_client_filters(self):
        qp = "query param!"
        uri_param = "uri param!"

        mock_empty = mock.Mock()
        mock_empty.status_code = 200
        mock_empty.links = {}
        mock_empty.json.return_value = {
            "resources": [
                {"a": "1", "b": "1"},
                {"a": "1", "b": "2"},
            ]
        }

        self.session.get.side_effect = [mock_empty]

        class Test(self.test_class):
            _query_mapping = resource.QueryParameters('a')
            base_path = "/%(something)s/blah"
            something = resource.URI("something")
            a = resource.Body("a")
            b = resource.Body("b")

        res = list(
            Test.list(
                self.session,
                paginated=True,
                query_param=qp,
                allow_unknown_params=True,
                something=uri_param,
                a='1',
                b='2',
            )
        )
        self.session.get.assert_called_once_with(
            f"/{uri_param}/blah",
            headers={'Accept': 'application/json'},
            microversion=None,
            params={'a': '1'},
        )
        self.assertEqual(1, len(res))
        self.assertEqual("2", res[0].b)

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

        results = list(
            Test.list(
                self.session,
                paginated=True,
                something=uri_param,
                **{qp_name: qp},
            )
        )

        self.assertEqual(1, len(results))

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.assertEqual(
            self.session.get.call_args_list[0][1]["params"], {qp_name: qp}
        )

        self.assertEqual(
            self.session.get.call_args_list[0][0][0],
            Test.base_path % {"something": uri_param},
        )

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

        results = list(
            Test.list(
                self.session,
                paginated=True,
                query_param=qp2,
                something=uri_param,
                **{qp_name: qp},
            )
        )

        self.assertEqual(1, len(results))

        # Look at the `params` argument to each of the get calls that
        # were made.
        self.assertEqual(
            self.session.get.call_args_list[0][1]["params"], {qp_name: qp2}
        )

        self.assertEqual(
            self.session.get.call_args_list[0][0][0],
            Test.base_path % {"something": uri_param},
        )

    def test_list_multi_page_response_paginated(self):
        ids = [1, 2]
        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.links = {}
        resp1.json.return_value = {
            "resources": [{"id": ids[0]}],
            "resources_links": [
                {
                    "href": "https://example.com/next-url",
                    "rel": "next",
                }
            ],
        }
        resp2 = mock.Mock()
        resp2.status_code = 200
        resp2.links = {}
        resp2.json.return_value = {
            "resources": [{"id": ids[1]}],
            "resources_links": [
                {
                    "href": "https://example.com/next-url",
                    "rel": "next",
                }
            ],
        }
        resp3 = mock.Mock()
        resp3.status_code = 200
        resp3.links = {}
        resp3.json.return_value = {"resources": []}

        self.session.get.side_effect = [resp1, resp2, resp3]

        results = self.sot.list(self.session, paginated=True)

        result0 = next(results)
        self.assertEqual(result0.id, ids[0])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={},
            microversion=None,
        )

        result1 = next(results)
        self.assertEqual(result1.id, ids[1])
        self.session.get.assert_called_with(
            'https://example.com/next-url',
            headers={"Accept": "application/json"},
            params={},
            microversion=None,
        )

        self.assertRaises(StopIteration, next, results)
        self.session.get.assert_called_with(
            'https://example.com/next-url',
            headers={"Accept": "application/json"},
            params={},
            microversion=None,
        )

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
            params={"limit": 3},
            microversion=None,
        )

        # Second page contains another two items
        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        result3 = next(results)
        self.assertEqual(result3.id, ids[3])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={"limit": 3, "marker": 2},
            microversion=None,
        )

        # Ensure we're done after those four items
        self.assertRaises(StopIteration, next, results)

        # Ensure we've given the last try to get more results
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={"limit": 3, "marker": 4},
            microversion=None,
        )

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
            params={"limit": 2},
            microversion=None,
        )

        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={'limit': 2, 'marker': 2},
            microversion=None,
        )

        # Ensure we're done after those three items
        # In python3.7, PEP 479 is enabled for all code, and StopIteration
        # raised directly from code is turned into a RuntimeError.
        # Something about how mock is implemented triggers that here.
        self.assertRaises((StopIteration, RuntimeError), next, results)

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
            params={},
            microversion=None,
        )

        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        self.session.get.assert_called_with(
            self.base_path,
            headers={"Accept": "application/json"},
            params={'marker': 2},
            microversion=None,
        )

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
            'next': {'uri': 'https://example.com/next-url', 'rel': 'next'}
        }
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
            params={},
            microversion=None,
        )

        result2 = next(results)
        self.assertEqual(result2.id, ids[2])
        self.session.get.assert_called_with(
            'https://example.com/next-url',
            headers={"Accept": "application/json"},
            params={},
            microversion=None,
        )

        # Ensure we're done after those three items
        self.assertRaises(StopIteration, next, results)

        # Ensure we only made two calls to get this done
        self.assertEqual(2, len(self.session.get.call_args_list))

    def test_bulk_create_invalid_data_passed(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'POST'
            allow_create = True

        Test._prepare_request = mock.Mock()
        self.assertRaises(ValueError, Test.bulk_create, self.session, [])
        self.assertRaises(ValueError, Test.bulk_create, self.session, None)
        self.assertRaises(ValueError, Test.bulk_create, self.session, object)
        self.assertRaises(ValueError, Test.bulk_create, self.session, {})
        self.assertRaises(ValueError, Test.bulk_create, self.session, "hi!")
        self.assertRaises(ValueError, Test.bulk_create, self.session, ["hi!"])

    def _test_bulk_create(
        self, cls, http_method, microversion=None, base_path=None, **params
    ):
        req1 = mock.Mock()
        req2 = mock.Mock()
        req1.body = {'name': 'resource1'}
        req2.body = {'name': 'resource2'}
        req1.url = 'uri'
        req2.url = 'uri'
        req1.headers = 'headers'
        req2.headers = 'headers'

        request_body = {
            "tests": [
                {'name': 'resource1', 'id': 'id1'},
                {'name': 'resource2', 'id': 'id2'},
            ]
        }

        cls._prepare_request = mock.Mock(side_effect=[req1, req2])
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.links = {}
        mock_response.json.return_value = request_body
        http_method.return_value = mock_response

        res = list(
            cls.bulk_create(
                self.session,
                [{'name': 'resource1'}, {'name': 'resource2'}],
                base_path=base_path,
                **params,
            )
        )

        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].id, 'id1')
        self.assertEqual(res[1].id, 'id2')
        http_method.assert_called_once_with(
            self.request.url,
            json={'tests': [req1.body, req2.body]},
            headers=self.request.headers,
            microversion=microversion,
            params=params,
        )

    def test_bulk_create_post(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'POST'
            allow_create = True
            resources_key = 'tests'

        self._test_bulk_create(Test, self.session.post)

    def test_bulk_create_put(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'PUT'
            allow_create = True
            resources_key = 'tests'

        self._test_bulk_create(Test, self.session.put)

    def test_bulk_create_with_params(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'POST'
            allow_create = True
            resources_key = 'tests'

        self._test_bulk_create(Test, self.session.post, answer=42)

    def test_bulk_create_with_microversion(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'POST'
            allow_create = True
            resources_key = 'tests'
            _max_microversion = '1.42'

        self._test_bulk_create(Test, self.session.post, microversion='1.42')

    def test_bulk_create_with_base_path(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'POST'
            allow_create = True
            resources_key = 'tests'

        self._test_bulk_create(Test, self.session.post, base_path='dummy')

    def test_bulk_create_fail(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'POST'
            allow_create = False
            resources_key = 'tests'

        self.assertRaises(
            exceptions.MethodNotSupported,
            Test.bulk_create,
            self.session,
            [{'name': 'name'}],
        )

    def test_bulk_create_fail_on_request(self):
        class Test(resource.Resource):
            service = self.service_name
            base_path = self.base_path
            create_method = 'POST'
            allow_create = True
            resources_key = 'tests'

        response = FakeResponse({}, status_code=409)
        response.content = (
            '{"TestError": {"message": "Failed to parse '
            'request. Required attribute \'foo\' not '
            'specified", "type": "HTTPBadRequest", '
            '"detail": ""}}'
        )
        response.reason = 'Bad Request'
        self.session.post.return_value = response
        self.assertRaises(
            exceptions.ConflictException,
            Test.bulk_create,
            self.session,
            [{'name': 'name'}],
        )


class TestResourceFind(base.TestCase):
    result = 1

    class Base(resource.Resource):
        @classmethod
        def existing(cls, **kwargs):
            response = mock.Mock()
            response.status_code = 404
            raise exceptions.NotFoundException('Not Found', response=response)

        @classmethod
        def list(cls, session, **params):
            return []

    class OneResult(Base):
        @classmethod
        def _get_one_match(cls, *args):
            return TestResourceFind.result

    class NoResults(Base):
        @classmethod
        def _get_one_match(cls, *args):
            return None

    class OneResultWithQueryParams(OneResult):
        _query_mapping = resource.QueryParameters('name')

    def setUp(self):
        super().setUp()
        self.no_results = self.NoResults
        self.one_result = self.OneResult
        self.one_result_with_qparams = self.OneResultWithQueryParams

    def test_find_short_circuit(self):
        value = 1

        class Test(resource.Resource):
            @classmethod
            def existing(cls, **kwargs):
                mock_match = mock.Mock()
                mock_match.fetch.return_value = value
                return mock_match

        result = Test.find(self.cloud.compute, "name")

        self.assertEqual(result, value)

    def test_no_match_raise(self):
        self.assertRaises(
            exceptions.NotFoundException,
            self.no_results.find,
            self.cloud.compute,
            "name",
            ignore_missing=False,
        )

    def test_no_match_return(self):
        self.assertIsNone(
            self.no_results.find(
                self.cloud.compute, "name", ignore_missing=True
            )
        )

    def test_find_result_name_not_in_query_parameters(self):
        with (
            mock.patch.object(
                self.one_result,
                'existing',
                side_effect=self.OneResult.existing,
            ) as mock_existing,
            mock.patch.object(
                self.one_result, 'list', side_effect=self.OneResult.list
            ) as mock_list,
        ):
            self.assertEqual(
                self.result, self.one_result.find(self.cloud.compute, "name")
            )
            mock_existing.assert_called_once_with(
                id='name', connection=mock.ANY
            )
            mock_list.assert_called_once_with(mock.ANY)

    def test_find_result_name_in_query_parameters(self):
        self.assertEqual(
            self.result,
            self.one_result_with_qparams.find(self.cloud.compute, "name"),
        )

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
            resource.Resource._get_one_match,
            the_id,
            [match, match],
        )

    def test_list_no_base_path(self):
        with mock.patch.object(self.Base, "list") as list_mock:
            self.Base.find(self.cloud.compute, "name")

            list_mock.assert_called_with(self.cloud.compute)

    def test_list_base_path(self):
        with mock.patch.object(self.Base, "list") as list_mock:
            self.Base.find(
                self.cloud.compute, "name", list_base_path='/dummy/list'
            )

            list_mock.assert_called_with(
                self.cloud.compute, base_path='/dummy/list'
            )


class TestWait(base.TestCase):
    def setUp(self):
        super().setUp()

        handler = logging.StreamHandler(self._log_stream)
        formatter = logging.Formatter('%(asctime)s %(name)-32s %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger('openstack.iterate_timeout')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    @staticmethod
    def _fake_resource(statuses=None, progresses=None, *, attribute='status'):
        if statuses is None:
            statuses = ['building', 'building', 'building', 'active']

        def fetch(*args, **kwargs):
            # when we get to the last status, keep returning that
            if statuses:
                setattr(fake_resource, attribute, statuses.pop(0))

            if progresses:
                fake_resource.progress = progresses.pop(0)

            return fake_resource

        spec = ['id', attribute, 'fetch']
        if progresses:
            spec.append('progress')

        fake_resource = mock.Mock(spec=spec)
        setattr(fake_resource, attribute, statuses.pop(0))
        fake_resource.fetch.side_effect = fetch

        return fake_resource


class TestWaitForStatus(TestWait):
    def test_immediate_status(self):
        status = "loling"
        res = mock.Mock(spec=['id', 'status'])
        res.status = status

        result = resource.wait_for_status(
            self.cloud.compute,
            res,
            status,
            None,
            interval=1,
            wait=1,
        )

        self.assertEqual(res, result)

    def test_immediate_status_case(self):
        status = "LOLing"
        res = mock.Mock(spec=['id', 'status'])
        res.status = status

        result = resource.wait_for_status(
            self.cloud.compute,
            res,
            'lOling',
            None,
            interval=1,
            wait=1,
        )

        self.assertEqual(res, result)

    def test_immediate_status_different_attribute(self):
        status = "loling"
        res = mock.Mock(spec=['id', 'mood'])
        res.mood = status

        result = resource.wait_for_status(
            self.cloud.compute,
            res,
            status,
            None,
            interval=1,
            wait=1,
            attribute='mood',
        )

        self.assertEqual(res, result)

    def test_status_match(self):
        status = "loling"

        # other gets past the first check, two anothers gets through
        # the sleep loop, and the third matches
        statuses = ["first", "other", "another", "another", status]
        res = self._fake_resource(statuses)

        result = resource.wait_for_status(
            mock.Mock(),
            res,
            status,
            None,
            interval=1,
            wait=5,
        )

        self.assertEqual(result, res)

    def test_status_match_with_none(self):
        status = "loling"

        # apparently, None is a correct state in some cases
        statuses = [None, "other", None, "another", status]
        res = self._fake_resource(statuses)

        result = resource.wait_for_status(
            mock.Mock(),
            res,
            status,
            None,
            interval=1,
            wait=5,
        )

        self.assertEqual(result, res)

    def test_status_match_none(self):
        status = None

        # apparently, None can be expected status in some cases
        statuses = ["first", "other", "another", "another", status]
        res = self._fake_resource(statuses)

        result = resource.wait_for_status(
            mock.Mock(),
            res,
            status,
            None,
            interval=1,
            wait=5,
        )

        self.assertEqual(result, res)

    def test_status_match_different_attribute(self):
        status = "loling"

        statuses = ["first", "other", "another", "another", status]
        res = self._fake_resource(statuses, attribute='mood')

        result = resource.wait_for_status(
            mock.Mock(),
            res,
            status,
            None,
            interval=1,
            wait=5,
            attribute='mood',
        )

        self.assertEqual(result, res)

    def test_status_fails(self):
        failure = "crying"

        statuses = ["success", "other", failure]
        res = self._fake_resource(statuses)

        self.assertRaises(
            exceptions.ResourceFailure,
            resource.wait_for_status,
            mock.Mock(),
            res,
            "loling",
            [failure],
            interval=1,
            wait=5,
        )

    def test_status_fails_different_attribute(self):
        failure = "crying"

        statuses = ["success", "other", failure]
        res = self._fake_resource(statuses, attribute='mood')

        self.assertRaises(
            exceptions.ResourceFailure,
            resource.wait_for_status,
            mock.Mock(),
            res,
            "loling",
            [failure.upper()],
            interval=1,
            wait=5,
            attribute='mood',
        )

    def test_timeout(self):
        status = "loling"

        # The first "other" gets past the first check, and then three
        # pairs of "other" statuses run through the sleep counter loop,
        # after which time should be up. This is because we have a
        # one second interval and three second waiting period.
        statuses = ["other"] * 7
        res = self._fake_resource(statuses)

        self.assertRaises(
            exceptions.ResourceTimeout,
            resource.wait_for_status,
            self.cloud.compute,
            res,
            status,
            None,
            0.01,
            0.1,
        )

    def test_no_sleep(self):
        statuses = ["other"]
        res = self._fake_resource(statuses)

        self.assertRaises(
            exceptions.ResourceTimeout,
            resource.wait_for_status,
            self.cloud.compute,
            res,
            "status",
            None,
            interval=0,
            wait=-1,
        )

    def test_callback(self):
        """Callback is called with 'progress' attribute."""
        statuses = ['building', 'building', 'building', 'building', 'active']
        progresses = [0, 25, 50, 100]
        res = self._fake_resource(statuses=statuses, progresses=progresses)

        callback = mock.Mock()

        result = resource.wait_for_status(
            mock.Mock(),
            res,
            'active',
            None,
            interval=0.1,
            wait=1,
            callback=callback,
        )

        self.assertEqual(result, res)
        callback.assert_has_calls([mock.call(x) for x in progresses])

    def test_callback_without_progress(self):
        """Callback is called with 0 if 'progress' attribute is missing."""
        statuses = ['building', 'building', 'building', 'building', 'active']
        res = self._fake_resource(statuses=statuses)

        callback = mock.Mock()

        result = resource.wait_for_status(
            mock.Mock(),
            res,
            'active',
            None,
            interval=0.1,
            wait=1,
            callback=callback,
        )

        self.assertEqual(result, res)
        # there are 5 statuses but only 3 callback calls since the initial
        # status and final status don't result in calls
        callback.assert_has_calls([mock.call(0)] * 3)


class TestWaitForDelete(TestWait):
    def test_success_not_found(self):
        response = mock.Mock()
        response.headers = {}
        response.status_code = 404
        res = mock.Mock()
        res.fetch.side_effect = [
            res,
            res,
            exceptions.NotFoundException('Not Found', response),
        ]

        result = resource.wait_for_delete(self.cloud.compute, res, 1, 3)

        self.assertEqual(result, res)

    def test_status(self):
        """Successful deletion indicated by status."""
        statuses = ['active', 'deleting', 'deleting', 'deleting', 'deleted']
        res = self._fake_resource(statuses=statuses)

        result = resource.wait_for_delete(
            mock.Mock(),
            res,
            interval=0.1,
            wait=1,
        )

        self.assertEqual(result, res)

    def test_callback(self):
        """Callback is called with 'progress' attribute."""
        statuses = ['active', 'deleting', 'deleting', 'deleting', 'deleted']
        progresses = [0, 25, 50, 100]
        res = self._fake_resource(statuses=statuses, progresses=progresses)

        callback = mock.Mock()

        result = resource.wait_for_delete(
            mock.Mock(),
            res,
            interval=1,
            wait=5,
            callback=callback,
        )

        self.assertEqual(result, res)
        callback.assert_has_calls([mock.call(x) for x in progresses])

    def test_callback_without_progress(self):
        """Callback is called with 0 if 'progress' attribute is missing."""
        statuses = ['active', 'deleting', 'deleting', 'deleting', 'deleted']
        res = self._fake_resource(statuses=statuses)

        callback = mock.Mock()

        result = resource.wait_for_delete(
            mock.Mock(),
            res,
            interval=1,
            wait=5,
            callback=callback,
        )

        self.assertEqual(result, res)
        # there are 5 statuses but only 3 callback calls since the initial
        # status and final status don't result in calls
        callback.assert_has_calls([mock.call(0)] * 3)

    def test_timeout(self):
        res = mock.Mock()
        res.status = 'ACTIVE'
        res.fetch.return_value = res

        self.assertRaises(
            exceptions.ResourceTimeout,
            resource.wait_for_delete,
            self.cloud.compute,
            res,
            0.1,
            0.3,
        )


@mock.patch.object(resource.Resource, '_get_microversion', autospec=True)
class TestAssertMicroversionFor(base.TestCase):
    session = mock.Mock()
    res = resource.Resource()

    def test_compatible(self, mock_get_ver):
        mock_get_ver.return_value = '1.42'

        self.assertEqual(
            '1.42',
            self.res._assert_microversion_for(self.session, '1.6'),
        )
        mock_get_ver.assert_called_once_with(self.session)

    def test_incompatible(self, mock_get_ver):
        mock_get_ver.return_value = '1.1'

        self.assertRaisesRegex(
            exceptions.NotSupported,
            '1.6 is required, but 1.1 will be used',
            self.res._assert_microversion_for,
            self.session,
            '1.6',
        )
        mock_get_ver.assert_called_once_with(self.session)

    def test_custom_message(self, mock_get_ver):
        mock_get_ver.return_value = '1.1'

        self.assertRaisesRegex(
            exceptions.NotSupported,
            'boom.*1.6 is required, but 1.1 will be used',
            self.res._assert_microversion_for,
            self.session,
            '1.6',
            error_message='boom',
        )
        mock_get_ver.assert_called_once_with(self.session)

    def test_none(self, mock_get_ver):
        mock_get_ver.return_value = None

        self.assertRaisesRegex(
            exceptions.NotSupported,
            '1.6 is required, but the default version',
            self.res._assert_microversion_for,
            self.session,
            '1.6',
        )
        mock_get_ver.assert_called_once_with(self.session)
