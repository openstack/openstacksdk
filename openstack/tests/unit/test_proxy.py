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

import mock
import testtools

from openstack import proxy
from openstack import resource


class Test_check_resource(testtools.TestCase):

    def setUp(self):
        super(Test_check_resource, self).setUp()

        def method(self, expected_type, value=None, *args, **kwargs):
            return value

        self.sot = mock.Mock()
        self.sot.method = method

    def _test_correct(self, value):
        decorated = proxy._check_resource(strict=False)(self.sot.method)
        rv = decorated(self.sot, resource.Resource, value)

        self.assertEqual(value, rv)

    def test_correct_resource(self):
        res = resource.Resource()
        self._test_correct(res)

    def test_notstrict_id(self):
        self._test_correct("abc123-id")

    def test_strict_id(self):
        decorated = proxy._check_resource(strict=True)(self.sot.method)
        self.assertRaisesRegexp(ValueError, "A Resource must be passed",
                                decorated, self.sot, resource.Resource,
                                "this-is-not-a-resource")

    def test_strict_None(self):
        # strict should only type check when `actual` is a value
        decorated = proxy._check_resource(strict=True)(self.sot.method)
        rv = decorated(self.sot, resource.Resource)

        self.assertIsNone(rv)

    def test_incorrect_resource(self):
        class OneType(resource.Resource):
            pass

        class AnotherType(resource.Resource):
            pass

        value = AnotherType()
        decorated = proxy._check_resource(strict=False)(self.sot.method)
        self.assertRaisesRegexp(ValueError,
                                "Expected OneType but received AnotherType",
                                decorated, self.sot, OneType, value)
