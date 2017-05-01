# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
import testtools

from openstack.metric.v1 import archive_policy

EXAMPLE = {
    'definition':
    [
        {u'points': 12, u'timespan': u'1:00:00',
         u'granularity': u'0:05:00'},
        {u'points': 24, u'timespan': u'1 day, 0:00:00',
         u'granularity': u'1:00:00'},
        {u'points': 30, u'timespan': u'30 days, 0:00:00',
         u'granularity': u'1 day, 0:00:00'},
    ],
    u'back_window': 0,
    u'name': u'low',
    u'aggregation_methods': [u'sum', u'max']
}


class TestArchivePolicy(testtools.TestCase):

    def setUp(self):
        super(TestArchivePolicy, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = ''
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)

    def test_basic(self):
        m = archive_policy.ArchivePolicy()
        self.assertIsNone(m.resource_key)
        self.assertIsNone(m.resources_key)
        self.assertEqual('/archive_policy', m.base_path)
        self.assertEqual('metric', m.service.service_type)
        self.assertTrue(m.allow_create)
        self.assertTrue(m.allow_get)
        self.assertFalse(m.allow_update)
        self.assertTrue(m.allow_delete)
        self.assertTrue(m.allow_list)

    def test_make_it(self):
        m = archive_policy.ArchivePolicy(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], m.name)
        self.assertEqual(EXAMPLE['name'], m.id)
        self.assertEqual(EXAMPLE['definition'], m.definition)
        self.assertEqual(EXAMPLE['back_window'], m.back_window)
        self.assertEqual(EXAMPLE['aggregation_methods'], m.aggregation_methods)
