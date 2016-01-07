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
import testtools

from openstack import format


class TestFormat(testtools.TestCase):
    def test_parse_true(self):
        self.assertTrue(format.BoolStr(True).parsed)
        self.assertTrue(format.BoolStr('True').parsed)
        self.assertTrue(format.BoolStr('TRUE').parsed)
        self.assertTrue(format.BoolStr('true').parsed)

    def test_parse_false(self):
        self.assertFalse(format.BoolStr(False).parsed)
        self.assertFalse(format.BoolStr('False').parsed)
        self.assertFalse(format.BoolStr('FALSE').parsed)
        self.assertFalse(format.BoolStr('false').parsed)

    def test_parse_fails(self):
        self.assertRaises(ValueError, format.BoolStr, None)
        self.assertRaises(ValueError, format.BoolStr, '')
        self.assertRaises(ValueError, format.BoolStr, 'INVALID')

    def test_to_str_true(self):
        self.assertEqual('True', str(format.BoolStr(True)))
        self.assertEqual('True', str(format.BoolStr('True')))

    def test_to_str_false(self):
        self.assertEqual('False', str(format.BoolStr('False')))
        self.assertEqual('False', str(format.BoolStr(False)))
