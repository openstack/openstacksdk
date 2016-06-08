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


class TestBoolStrFormatter(testtools.TestCase):

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

    def test_serialize(self):
        self.assertEqual('true', format.BoolStr.serialize(True))
        self.assertEqual('false', format.BoolStr.serialize(False))
        self.assertRaises(ValueError, format.BoolStr.serialize, None)
        self.assertRaises(ValueError, format.BoolStr.serialize, '')
        self.assertRaises(ValueError, format.BoolStr.serialize, 'True')
