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

from openstack import fields
from openstack import format
from openstack import resource
from openstack.tests.unit import base


class TestConvertValue(base.TestCase):
    def test_convert_value(self):
        class FakeResource(resource.Resource):
            abc = fields.Body('abc', type=int)

        test_data = [
            {
                'name': 'no data_type',
                'value': '123',
                'data_type': None,
                'expected': '123',
            },
            {
                'name': 'convert list to list with no list_type',
                'value': ['123'],
                'data_type': list,
                'expected': ['123'],
            },
            {
                'name': 'convert tuple to list with no list_type',
                'value': ('123',),
                'data_type': list,
                'expected': ['123'],
            },
            {
                'name': 'convert set to list with no list_type',
                'value': {'123'},
                'data_type': list,
                'expected': ['123'],
            },
            {
                'name': 'convert list to list with list_type',
                'value': ['123'],
                'data_type': list,
                'list_type': int,
                'expected': [123],
            },
            {
                'name': 'convert tuple to list with list_type',
                'value': ('123',),
                'data_type': list,
                'list_type': int,
                'expected': [123],
            },
            {
                'name': 'convert set to list with list_type',
                'value': {'123'},
                'data_type': list,
                'list_type': int,
                'expected': [123],
            },
            {
                'name': 'convert with formatter',
                'value': 'true',
                'data_type': format.BoolStr,
                'expected': True,
            },
            {
                'name': 'convert to resource',
                'value': {'abc': '123'},
                'data_type': FakeResource,
                # NOTE(stephenfin): The Resource.__eq__ compares the underlying
                # value types, not the converted value types, so we need a
                # string here
                'expected': FakeResource(abc='123'),
            },
            {
                'name': 'convert string to int',
                'value': '123',
                'data_type': int,
                'expected': 123,
            },
            {
                'name': 'convert invalid string to int',
                'value': 'abc',
                'data_type': int,
                'expected': 0,
            },
            {
                'name': 'convert valid int to string',
                'value': 123,
                'data_type': str,
                'expected': '123',
            },
            {
                'name': 'convert string to bool',
                'value': 'anything',
                'data_type': bool,
                'expected': True,
            },
        ]

        for data in test_data:
            with self.subTest(msg=data['name']):
                ret = fields._convert_type(
                    data['value'], data['data_type'], data.get('list_type')
                )
                self.assertEqual(ret, data['expected'])


class TestComponent(base.TestCase):
    class ExampleComponent(fields._BaseComponent):
        key = "_example"

    # Since we're testing ExampleComponent, which is as isolated as we
    # can test _BaseComponent due to it's needing to be a data member
    # of a class that has an attribute on the parent class named `key`,
    # each test has to implement a class with a name that is the same
    # as ExampleComponent.key, which should be a dict containing the
    # keys and values to test against.

    def test_implementations(self):
        self.assertEqual("_body", fields.Body.key)
        self.assertEqual("_header", fields.Header.key)
        self.assertEqual("_uri", fields.URI.key)

    def test_creation(self):
        sot = fields._BaseComponent(
            "name", type=int, default=1, alternate_id=True, aka="alias"
        )

        self.assertEqual("name", sot.name)
        self.assertEqual(int, sot.type)
        self.assertEqual(1, sot.default)
        self.assertEqual("alias", sot.aka)
        self.assertTrue(sot.alternate_id)

    def test_get_no_instance(self):
        sot = fields._BaseComponent("test")

        # Test that we short-circuit everything when given no instance.
        result = sot.__get__(None, None)
        self.assertIs(sot, result)

    # NOTE: Some tests will use a default=1 setting when testing result
    # values that should be None because the default-for-default is also None.
    def test_get_name_None(self):
        name = "name"

        class Parent:
            _example = {name: None}

        instance = Parent()
        sot = TestComponent.ExampleComponent(name, default=1)

        # Test that we short-circuit any typing of a None value.
        result = sot.__get__(instance, None)
        self.assertIsNone(result)

    def test_get_default(self):
        expected_result = 123

        class Parent:
            _example = {}

        instance = Parent()
        # NOTE: type=dict but the default value is an int. If we didn't
        # short-circuit the typing part of __get__ it would fail.
        sot = TestComponent.ExampleComponent(
            "name", type=dict, default=expected_result
        )

        # Test that we directly return any default value.
        result = sot.__get__(instance, None)
        self.assertEqual(expected_result, result)

    def test_get_name_untyped(self):
        name = "name"
        expected_result = 123

        class Parent:
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

        class Parent:
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

        class Parent:
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

        class Parent:
            _example = {}

        instance = Parent()
        sot = TestComponent.ExampleComponent("name")

        # Test that we don't run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual(expected_value, instance._example[name])

    def test_set_name_typed(self):
        expected_value = "123"

        class Parent:
            _example = {}

        instance = Parent()

        # The type we give to ExampleComponent has to be an actual type,
        # not an instance, so we can't get the niceties of a mock.Mock
        # instance that would allow us to call `assert_called_once_with` to
        # ensure that we're sending the value through the type.
        # Instead, we use this tiny version of a similar thing.
        class FakeType:
            calls = []

            def __init__(self, arg):
                FakeType.calls.append(arg)

        sot = TestComponent.ExampleComponent("name", type=FakeType)

        # Test that we run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual([expected_value], FakeType.calls)

    def test_set_name_formatter(self):
        expected_value = "123"

        class Parent:
            _example = {}

        instance = Parent()

        # As with test_set_name_typed, create a pseudo-Mock to track what
        # gets called on the type.
        class FakeFormatter(format.Formatter):
            calls = []

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

        class Parent:
            _example = {name: expected_value}

        instance = Parent()

        sot = TestComponent.ExampleComponent("name")

        sot.__delete__(instance)

        self.assertNotIn(name, instance._example)

    def test_delete_name_doesnt_exist(self):
        name = "name"
        expected_value = "123"

        class Parent:
            _example = {"what": expected_value}

        instance = Parent()

        sot = TestComponent.ExampleComponent(name)

        sot.__delete__(instance)

        self.assertNotIn(name, instance._example)
