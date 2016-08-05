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

from openstack.orchestration.v1 import resource


FAKE_ID = '32e39358-2422-4ad0-a1b5-dd60696bf564'
FAKE_NAME = 'test_stack'
FAKE = {
    'links': [{
        'href': 'http://res_link',
        'rel': 'self'
    }, {
        'href': 'http://stack_link',
        'rel': 'stack'
    }],
    'logical_resource_id': 'the_resource',
    'name': 'the_resource',
    'physical_resource_id': '9f38ab5a-37c8-4e40-9702-ce27fc5f6954',
    'required_by': [],
    'resource_type': 'OS::Heat::FakeResource',
    'status': 'CREATE_COMPLETE',
    'status_reason': 'state changed',
    'updated_time': '2015-03-09T12:15:57.233772',
}


class TestResource(testtools.TestCase):

    def test_basic(self):
        sot = resource.Resource()
        self.assertEqual('resource', sot.resource_key)
        self.assertEqual('resources', sot.resources_key)
        self.assertEqual('/stacks/%(stack_name)s/%(stack_id)s/resources',
                         sot.base_path)
        self.assertEqual('orchestration', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = resource.Resource(**FAKE)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['logical_resource_id'], sot.logical_resource_id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['physical_resource_id'],
                         sot.physical_resource_id)
        self.assertEqual(FAKE['required_by'], sot.required_by)
        self.assertEqual(FAKE['resource_type'], sot.resource_type)
        self.assertEqual(FAKE['status'], sot.status)
        self.assertEqual(FAKE['status_reason'], sot.status_reason)
        self.assertEqual(FAKE['updated_time'], sot.updated_at)
