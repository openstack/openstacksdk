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

from openstack.compute.v2 import volume_attachment

EXAMPLE = {
    'device': '1',
    'id': '2',
    'volume_id': '3',
}


class TestServerInterface(base.TestCase):

    def test_basic(self):
        sot = volume_attachment.VolumeAttachment()
        self.assertEqual('volumeAttachment', sot.resource_key)
        self.assertEqual('volumeAttachments', sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/os-volume_attachments',
                         sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertDictEqual({"limit": "limit",
                              "offset": "offset",
                              "marker": "marker"},
                             sot._query_mapping._mapping)

    def test_make_it(self):
        sot = volume_attachment.VolumeAttachment(**EXAMPLE)
        self.assertEqual(EXAMPLE['device'], sot.device)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['volume_id'], sot.volume_id)
