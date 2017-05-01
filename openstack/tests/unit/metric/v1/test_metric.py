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

from openstack.metric.v1 import metric

EXAMPLE = {
    'id': '31bbd62e-b144-11e4-983c-bf9dbe7e25e6',
    'archive_policy_name': 'low',
    'created_by_user_id': '41bbd62e-b144-11e4-983c-bf9dbe7e25e6',
    'created_by_project_id': '51bbd62e-b144-11e4-983c-bf9dbe7e25e6',
    'resource_id': None,
    'name': None,
}

EXAMPLE_AP = {
    'id': '31bbd62e-b144-11e4-983c-bf9dbe7e25e6',
    'archive_policy': {
        'name': "foobar",
    },
    'created_by_user_id': '41bbd62e-b144-11e4-983c-bf9dbe7e25e6',
    'created_by_project_id': '51bbd62e-b144-11e4-983c-bf9dbe7e25e6',
    'resource_id': "61bbd62e-b144-11e4-983c-bf9dbe7e25e6",
    'name': "foobaz",
}


class TestMetric(testtools.TestCase):

    def setUp(self):
        super(TestMetric, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = ''
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)

    def test_basic(self):
        m = metric.Metric()
        self.assertIsNone(m.resource_key)
        self.assertIsNone(m.resources_key)
        self.assertEqual('/metric', m.base_path)
        self.assertEqual('metric', m.service.service_type)
        self.assertTrue(m.allow_create)
        self.assertTrue(m.allow_get)
        self.assertFalse(m.allow_update)
        self.assertTrue(m.allow_delete)
        self.assertTrue(m.allow_list)

    def test_make_it(self):
        m = metric.Metric(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], m.id)
        self.assertEqual(EXAMPLE['archive_policy_name'], m.archive_policy_name)
        self.assertEqual(EXAMPLE['created_by_user_id'], m.created_by_user_id)
        self.assertEqual(EXAMPLE['created_by_project_id'],
                         m.created_by_project_id)
        self.assertEqual(EXAMPLE['resource_id'], m.resource_id)
        self.assertEqual(EXAMPLE['name'], m.name)

        m = metric.Metric(**EXAMPLE_AP)
        self.assertEqual(EXAMPLE_AP['id'], m.id)
        self.assertEqual(EXAMPLE_AP['archive_policy'], m.archive_policy)
        self.assertEqual(EXAMPLE_AP['created_by_user_id'],
                         m.created_by_user_id)
        self.assertEqual(EXAMPLE_AP['created_by_project_id'],
                         m.created_by_project_id)
        self.assertEqual(EXAMPLE_AP['resource_id'], m.resource_id)
        self.assertEqual(EXAMPLE_AP['name'], m.name)
