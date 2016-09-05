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

from openstack.telemetry.v2 import resource

IDENTIFIER = 'IDENTIFIER'
LINKS = [{'href': 'first_uri', 'rel': 'label 1', },
         {'href': 'other_uri', 'rel': 'label', }, ]
EXAMPLE = {
    'resource_id': IDENTIFIER,
    'first_sample_timestamp': '2015-03-09T12:15:57.233772',
    'last_sample_timestamp': '2015-03-09T12:15:57.233772',
    'links': LINKS,
    'metadata': {'name_one': '1', 'name_two': '2', },
    'project_id': '123',
    'source': 'abc',
    'user_id': '789'
}


class TestResource(testtools.TestCase):

    def test_basic(self):
        sot = resource.Resource()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/resources', sot.base_path)
        self.assertEqual('metering', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = resource.Resource(**EXAMPLE)
        self.assertEqual(EXAMPLE['resource_id'], sot.id)
        self.assertEqual(EXAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(EXAMPLE['first_sample_timestamp'],
                         sot.first_sample_at)
        self.assertEqual(EXAMPLE['last_sample_timestamp'],
                         sot.last_sample_at)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)
        self.assertEqual(EXAMPLE['project_id'], sot.project_id)
        self.assertEqual(EXAMPLE['resource_id'], sot.resource_id)
        self.assertEqual(EXAMPLE['source'], sot.source)
        self.assertEqual(EXAMPLE['user_id'], sot.user_id)
