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
        class Fake(resource.Resource):
            a = resource.Body("a", type=str)
            b = resource.Body("b", type=int)
            c = resource.Body("c", type=bool)
            d = resource.Body("d", type=_format.BoolStr)
            e = resource.Body("e", type=dict)
            f = resource.URI("path")

        res = fakes.generate_fake_resource(Fake)
        self.assertIsInstance(res.a, str)
        self.assertIsInstance(res.b, int)
        self.assertIsInstance(res.c, bool)
        self.assertIsInstance(res.d, bool)
        self.assertIsInstance(res.e, dict)
        self.assertIsInstance(res.f, str)

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
