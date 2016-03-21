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

from datetime import datetime
from iso8601 import iso8601
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


class TestISO8601Formatter(testtools.TestCase):

    def test_deserialize(self):
        self.assertEqual(
            format.ISO8601.deserialize("2015-06-27T05:09:43"),
            datetime(2015, 6, 27, 5, 9, 43, tzinfo=iso8601.UTC))
        self.assertEqual(
            format.ISO8601.deserialize("2012-03-28T21:31:02Z"),
            datetime(2012, 3, 28, 21, 31, 2, tzinfo=iso8601.UTC))
        self.assertEqual(
            format.ISO8601.deserialize("2013-09-23T13:53:12.774549"),
            datetime(2013, 9, 23, 13, 53, 12, 774549, tzinfo=iso8601.UTC))
        self.assertEqual(
            format.ISO8601.deserialize("2015-08-27T09:49:58-05:00"),
            datetime(2015, 8, 27, 9, 49, 58,
                     tzinfo=iso8601.FixedOffset(-5, 0, "-05:00")))

    def test_serialize(self):
        self.assertEqual(
            format.ISO8601.serialize(
                datetime(2015, 6, 27, 5, 9, 43, tzinfo=iso8601.UTC)),
            "2015-06-27T05:09:43+00:00")
        self.assertEqual(
            format.ISO8601.serialize(
                datetime(2012, 3, 28, 21, 31, 2, tzinfo=iso8601.UTC)),
            "2012-03-28T21:31:02+00:00")
        self.assertEqual(
            format.ISO8601.serialize(
                datetime(2013, 9, 23, 13, 53, 12, 774549, tzinfo=iso8601.UTC)),
            "2013-09-23T13:53:12.774549+00:00")
        self.assertEqual(
            format.ISO8601.serialize(
                datetime(2015, 8, 27, 9, 49, 58,
                         tzinfo=iso8601.FixedOffset(-5, 0, "-05:00"))),
            "2015-08-27T09:49:58-05:00")


class TestUNIXEpochFormatter(testtools.TestCase):

    def test_deserialize(self):
        self.assertEqual(format.UNIXEpoch.deserialize(1453412616.02406),
                         datetime(2016, 1, 21, 21, 43, 36, 24060,
                                  tzinfo=iso8601.UTC))
        self.assertEqual(format.UNIXEpoch.deserialize(1389453423.35964),
                         datetime(2014, 1, 11, 15, 17, 3, 359640,
                                  tzinfo=iso8601.UTC))
        self.assertEqual(format.UNIXEpoch.deserialize(1389453423),
                         datetime(2014, 1, 11, 15, 17, 3, tzinfo=iso8601.UTC))
        self.assertRaises(ValueError, format.UNIXEpoch.deserialize, "lol")

    def test_serialize(self):
        self.assertEqual(
            format.UNIXEpoch.serialize(
                datetime(2016, 1, 21, 21, 43, 36, 24060, tzinfo=iso8601.UTC)),
            1453412616.02406)
        self.assertEqual(
            format.UNIXEpoch.serialize(
                datetime(2014, 1, 11, 15, 17, 3, 359640, tzinfo=iso8601.UTC)),
            1389453423.35964)
        self.assertEqual(
            format.UNIXEpoch.serialize(
                datetime(2014, 1, 11, 15, 17, 3, tzinfo=iso8601.UTC)),
            1389453423)
        self.assertRaises(ValueError, format.UNIXEpoch.serialize, "lol")
