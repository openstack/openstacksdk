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

from openstack import format as _format
from openstack import resource
from openstack.test import fakes
from openstack.tests.unit import base


class TestGetFake(base.TestCase):
    def test_generate_fake_resource_one(self):
        res = fakes.generate_fake_resource(resource.Resource)
        self.assertIsInstance(res, resource.Resource)

    def test_generate_fake_resource_list(self):
        res = list(fakes.generate_fake_resources(resource.Resource, 2))
        self.assertEqual(2, len(res))
        self.assertIsInstance(res[0], resource.Resource)

    def test_generate_fake_resource_types(self):
        class Foo(resource.Resource):
            a = resource.Body("a", type=str)
            b = resource.Body("b", type=int)
            c = resource.Body("c", type=bool)
            d = resource.Body("d", type=_format.BoolStr)
            e = resource.Body("e", type=dict)
            f = resource.URI("path")

        class Bar(resource.Resource):
            a = resource.Body("a", type=list, list_type=str)
            b = resource.Body("b", type=list, list_type=dict)
            c = resource.Body("c", type=list, list_type=Foo)

        foo = fakes.generate_fake_resource(Foo)
        self.assertIsInstance(foo.a, str)
        self.assertIsInstance(foo.b, int)
        self.assertIsInstance(foo.c, bool)
        self.assertIsInstance(foo.d, bool)
        self.assertIsInstance(foo.e, dict)
        self.assertIsInstance(foo.f, str)

        bar = fakes.generate_fake_resource(Bar)
        self.assertIsInstance(bar.a, list)
        self.assertEqual(1, len(bar.a))
        self.assertIsInstance(bar.a[0], str)
        self.assertIsInstance(bar.b, list)
        self.assertEqual(1, len(bar.b))
        self.assertIsInstance(bar.b[0], dict)
        self.assertIsInstance(bar.c, list)
        self.assertEqual(1, len(bar.c))
        self.assertIsInstance(bar.c[0], Foo)
        self.assertIsInstance(bar.c[0].a, str)
        self.assertIsInstance(bar.c[0].b, int)
        self.assertIsInstance(bar.c[0].c, bool)
        self.assertIsInstance(bar.c[0].d, bool)
        self.assertIsInstance(bar.c[0].e, dict)
        self.assertIsInstance(bar.c[0].f, str)

    def test_generate_fake_resource_attrs(self):
        class Fake(resource.Resource):
            a = resource.Body("a", type=str)
            b = resource.Body("b", type=str)

        res = fakes.generate_fake_resource(Fake, b="bar")
        self.assertIsInstance(res.a, str)
        self.assertIsInstance(res.b, str)
        self.assertEqual("bar", res.b)

    def test_generate_fake_resource_types_inherit(self):
        class Fake(resource.Resource):
            a = resource.Body("a", type=str)

        class FakeInherit(resource.Resource):
            a = resource.Body("a", type=Fake)

        res = fakes.generate_fake_resource(FakeInherit)
        self.assertIsInstance(res.a, Fake)
        self.assertIsInstance(res.a.a, str)

    def test_unknown_attrs_as_props(self):
        class Fake(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        res = fakes.generate_fake_resource(Fake)
        self.assertIsInstance(res.properties, dict)
