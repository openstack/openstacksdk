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

from openstack.compute.v2 import server_share
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "uuid": "715335c1-7a00-4dfe-82df-9dc2a67bd8bf",
    "share_id": "e8debdc0-447a-4376-a10a-4cd9122d7986",
    "share_proto": "NFS",
    "status": "active",
    "tag": "bar",
    "export_location": "server.com/nfs_mount,foo=bar",
}


class TestServerShare(base.TestCase):
    def test_basic(self):
        sot = server_share.ShareMapping()
        self.assertEqual('share', sot.resource_key)
        self.assertEqual('shares', sot.resources_key)
        self.assertEqual('/servers/%(server_id)s/shares', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = server_share.ShareMapping(**EXAMPLE)
        self.assertEqual(EXAMPLE['uuid'], sot.uuid)
        self.assertEqual(EXAMPLE['share_id'], sot.share_id)
        self.assertEqual(EXAMPLE['share_id'], sot.id)
        self.assertEqual(EXAMPLE['share_proto'], sot.share_proto)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['tag'], sot.tag)
        self.assertEqual(EXAMPLE['export_location'], sot.export_location)
