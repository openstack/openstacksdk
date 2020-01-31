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

from openstack.tests.unit import base

from openstack.accelerator.v2 import accelerator_request as arq

FAKE_ID = '0725b527-e51a-41df-ad22-adad5f4546ad'
FAKE_RP_UUID = 'f4b7fe6c-8ab4-4914-a113-547af022935b'
FAKE_INSTANCE_UUID = '1ce4a597-9836-4e02-bea1-a3a6cbe7b9f9'
FAKE_ATTACH_INFO_STR = '{"bus": "5e", '\
    '"device": "00", '\
    '"domain": "0000", '\
    '"function": "1"}'

FAKE = {
    'uuid': FAKE_ID,
    'device_profile_name': 'fake-devprof',
    'device_profile_group_id': 0,
    'device_rp_uuid': FAKE_RP_UUID,
    'instance_uuid': FAKE_INSTANCE_UUID,
    'attach_handle_type': 'PCI',
    'attach_handle_info': FAKE_ATTACH_INFO_STR,
}


class TestAcceleratorRequest(base.TestCase):

    def test_basic(self):
        sot = arq.AcceleratorRequest()
        self.assertEqual('arq', sot.resource_key)
        self.assertEqual('arqs', sot.resources_key)
        self.assertEqual('/accelerator_requests', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_patch)

    def test_make_it(self):
        sot = arq.AcceleratorRequest(**FAKE)
        self.assertEqual(FAKE_ID, sot.uuid)
        self.assertEqual(FAKE['device_profile_name'], sot.device_profile_name)
        self.assertEqual(FAKE['device_profile_group_id'],
                         sot.device_profile_group_id)
        self.assertEqual(FAKE_RP_UUID, sot.device_rp_uuid)
        self.assertEqual(FAKE_INSTANCE_UUID, sot.instance_uuid)
        self.assertEqual(FAKE['attach_handle_type'], sot.attach_handle_type)
        self.assertEqual(FAKE_ATTACH_INFO_STR, sot.attach_handle_info)
