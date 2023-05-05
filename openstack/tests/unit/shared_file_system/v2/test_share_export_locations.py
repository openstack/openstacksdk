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

from openstack.shared_file_system.v2 import share_export_locations as el
from openstack.tests.unit import base


IDENTIFIER = '08a87d37-5ca2-4308-86c5-cba06d8d796c'
EXAMPLE = {
    "id": "f87589cb-f4bc-4a9b-b481-ab701206eb85",
    "path": (
        "199.19.213.225:/opt/stack/data/manila/mnt/"
        "share-6ba490c5-5225-4c3b-9982-14b8f475c6d9"
    ),
    "preferred": False,
    "share_instance_id": "6ba490c5-5225-4c3b-9982-14b8f475c6d9",
    "is_admin_only": False,
}


class TestShareExportLocations(base.TestCase):
    def test_basic(self):
        export = el.ShareExportLocation()
        self.assertEqual('export_locations', export.resources_key)
        self.assertEqual(
            '/shares/%(share_id)s/export_locations', export.base_path
        )
        self.assertTrue(export.allow_list)

    def test_share_export_locations(self):
        export = el.ShareExportLocation(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], export.id)
        self.assertEqual(EXAMPLE['path'], export.path)
        self.assertEqual(EXAMPLE['preferred'], export.is_preferred)
        self.assertEqual(
            EXAMPLE['share_instance_id'], export.share_instance_id
        )
        self.assertEqual(EXAMPLE['is_admin_only'], export.is_admin)
