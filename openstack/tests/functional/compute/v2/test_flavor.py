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

import six

from openstack import exceptions
from openstack.tests.functional import base


class TestFlavor(base.BaseFunctionalTest):

    def setUp(self):
        super(TestFlavor, self).setUp()

        self.one_flavor = list(self.conn.compute.flavors())[0]

    def test_flavors(self):
        flavors = list(self.conn.compute.flavors())
        self.assertGreater(len(flavors), 0)

        for flavor in flavors:
            self.assertIsInstance(flavor.id, six.string_types)
            self.assertIsInstance(flavor.name, six.string_types)
            self.assertIsInstance(flavor.disk, int)
            self.assertIsInstance(flavor.ram, int)
            self.assertIsInstance(flavor.vcpus, int)

    def test_find_flavors_by_id(self):
        rslt = self.conn.compute.find_flavor(self.one_flavor.id)
        self.assertEqual(rslt.id, self.one_flavor.id)

    def test_find_flavors_by_name(self):
        rslt = self.conn.compute.find_flavor(self.one_flavor.name)
        self.assertEqual(rslt.name, self.one_flavor.name)

    def test_find_flavors_no_match_ignore_true(self):
        rslt = self.conn.compute.find_flavor("not a flavor",
                                             ignore_missing=True)
        self.assertIsNone(rslt)

    def test_find_flavors_no_match_ignore_false(self):
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.compute.find_flavor,
                          "not a flavor", ignore_missing=False)
