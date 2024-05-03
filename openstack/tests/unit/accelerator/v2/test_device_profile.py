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

from openstack.accelerator.v2 import device_profile
from openstack.tests.unit import base


FAKE = {
    "id": 1,
    "uuid": "a95e10ae-b3e3-4eab-a513-1afae6f17c51",
    "name": 'afaas_example_1',
    "groups": [
        {
            "resources:ACCELERATOR_FPGA": "1",
            "trait:CUSTOM_FPGA_INTEL_PAC_ARRIA10": "required",
            "trait:CUSTOM_FUNCTION_ID_3AFB": "required",
        },
        {
            "resources:CUSTOM_ACCELERATOR_FOO": "2",
            "resources:CUSTOM_MEMORY": "200",
            "trait:CUSTOM_TRAIT_ALWAYS": "required",
        },
    ],
    'description': 'description_test',
}


class TestDeviceProfile(base.TestCase):
    def test_basic(self):
        sot = device_profile.DeviceProfile()
        self.assertEqual('device_profile', sot.resource_key)
        self.assertEqual('device_profiles', sot.resources_key)
        self.assertEqual('/device_profiles', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_patch)

    def test_make_it(self):
        sot = device_profile.DeviceProfile(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['uuid'], sot.uuid)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['groups'], sot.groups)
        self.assertEqual(FAKE['description'], sot.description)
