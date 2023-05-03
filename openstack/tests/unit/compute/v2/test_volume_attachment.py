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

from openstack.compute.v2 import volume_attachment
from openstack.tests.unit import base


EXAMPLE = {
    'attachment_id': '979ce4f8-033a-409d-85e6-6b5c0f6a6302',
    'delete_on_termination': False,
    'device': '/dev/sdc',
    'serverId': '7696780b-3f53-4688-ab25-019bfcbbd806',
    'tag': 'foo',
    'volumeId': 'a07f71dc-8151-4e7d-a0cc-cd24a3f11113',
    'bdm_uuid': 'c088db45-92b8-49e8-81e2-a1b77a144b3b',
}


class TestServerInterface(base.TestCase):
    def test_basic(self):
        sot = volume_attachment.VolumeAttachment()
        self.assertEqual('volumeAttachment', sot.resource_key)
        self.assertEqual('volumeAttachments', sot.resources_key)
        self.assertEqual(
            '/servers/%(server_id)s/os-volume_attachments',
            sot.base_path,
        )
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertDictEqual(
            {"limit": "limit", "offset": "offset", "marker": "marker"},
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = volume_attachment.VolumeAttachment(**EXAMPLE)
        self.assertEqual(EXAMPLE['volumeId'], sot.id)
        self.assertEqual(EXAMPLE['attachment_id'], sot.attachment_id)
        self.assertEqual(
            EXAMPLE['delete_on_termination'],
            sot.delete_on_termination,
        )
        self.assertEqual(EXAMPLE['device'], sot.device)
        # FIXME(stephenfin): This conflicts since there is a server ID in the
        # URI *and* in the body. We need a field that handles both or we need
        # to use different names.
        # self.assertEqual(EXAMPLE['serverId'], sot.server_id)
        self.assertEqual(EXAMPLE['tag'], sot.tag)
        self.assertEqual(EXAMPLE['volumeId'], sot.volume_id)
        self.assertEqual(EXAMPLE['bdm_uuid'], sot.bdm_id)
