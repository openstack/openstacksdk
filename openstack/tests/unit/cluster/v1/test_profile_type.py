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

from openstack.cluster.v1 import profile_type


FAKE = {
    'name': 'FAKE_PROFILE_TYPE',
    'schema': {
        'foo': 'bar'
    }
}


class TestProfileType(testtools.TestCase):

    def test_basic(self):
        sot = profile_type.ProfileType()
        self.assertEqual('name', sot.id_attribute)
        self.assertEqual('profile_type', sot.resource_key)
        self.assertEqual('profile_types', sot.resources_key)
        self.assertEqual('/profile-types', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = profile_type.ProfileType(FAKE)
        self.assertEqual(FAKE['name'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['schema'], sot.schema)
