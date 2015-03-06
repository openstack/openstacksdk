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
import datetime

import testtools

from openstack.metric.v1 import resource


EXAMPLE_GENERIC = {
    "created_by_user_id": "5521eab6-a3bc-4841-b253-d62871b65e76",
    "started_at": "2015-03-09T12:14:57.233772",
    "user_id": None,
    "created_by_project_id": "41649c3e-5f7a-41d1-81fb-2efa76c09e6c",
    "metrics": {},
    "ended_at": None,
    "project_id": None,
    "type": "generic",
    "id": "a8d5e83b-0320-45ce-8282-7c8ad8fb8bf6",
}


class TestResource(testtools.TestCase):
    def test_generic(self):
        m = resource.Generic()
        self.assertIsNone(m.resource_key)
        self.assertIsNone(m.resources_key)
        self.assertEqual('/resource/generic', m.base_path)
        self.assertEqual('metric', m.service.service_type)
        self.assertTrue(m.allow_create)
        self.assertTrue(m.allow_retrieve)
        self.assertTrue(m.allow_update)
        self.assertTrue(m.allow_delete)
        self.assertTrue(m.allow_list)

    def test_make_generic(self):
        r = resource.Generic(EXAMPLE_GENERIC)
        self.assertEqual(EXAMPLE_GENERIC['created_by_user_id'],
                         r.created_by_user_id)
        self.assertEqual(EXAMPLE_GENERIC['created_by_project_id'],
                         r.created_by_project_id)
        self.assertEqual(EXAMPLE_GENERIC['user_id'], r.user_id)
        self.assertEqual(EXAMPLE_GENERIC['project_id'], r.project_id)
        self.assertEqual(EXAMPLE_GENERIC['type'], r.type)
        self.assertEqual(EXAMPLE_GENERIC['id'], r.id)
        self.assertEqual(EXAMPLE_GENERIC['metrics'], r.metrics)
        dt = datetime.datetime(2015, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, r.started_at.replace(tzinfo=None))
        self.assertEqual(EXAMPLE_GENERIC['ended_at'], r.ended_at)
