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

from openstack import format
from openstack.tests.unit import base


class TestBoolStrFormatter(base.TestCase):
    def test_deserialize(self):
        self.assertTrue(format.BoolStr.deserialize(True))
        self.assertTrue(format.BoolStr.deserialize('True'))
        self.assertTrue(format.BoolStr.deserialize('TRUE'))
        self.assertTrue(format.BoolStr.deserialize('true'))
        self.assertFalse(format.BoolStr.deserialize(False))
        self.assertFalse(format.BoolStr.deserialize('False'))
        self.assertFalse(format.BoolStr.deserialize('FALSE'))
        self.assertFalse(format.BoolStr.deserialize('false'))
        self.assertRaises(ValueError, format.BoolStr.deserialize, None)
        self.assertRaises(ValueError, format.BoolStr.deserialize, '')
        self.assertRaises(ValueError, format.BoolStr.deserialize, 'INVALID')


class TestFlexibleBoolStrFormatter(base.TestCase):
    def test_deserialize_true(self):
        for value in (
            True,
            '1',
            't',
            'T',
            'true',
            'True',
            'TRUE',
            'on',
            'ON',
            'y',
            'Y',
            'yes',
            'Yes',
            ' yes ',
        ):
            self.assertIs(
                True, format.FlexibleBoolStr.deserialize(value), repr(value)
            )

    def test_deserialize_false(self):
        for value in (
            False,
            '0',
            'f',
            'F',
            'false',
            'False',
            'FALSE',
            'off',
            'OFF',
            'n',
            'N',
            'no',
            'No',
            ' no ',
        ):
            self.assertIs(
                False, format.FlexibleBoolStr.deserialize(value), repr(value)
            )

    def test_deserialize_unrecognised(self):
        for value in (None, '', 'INVALID', '2', 'enabled', 'maybe'):
            self.assertIs(
                False, format.FlexibleBoolStr.deserialize(value), repr(value)
            )
