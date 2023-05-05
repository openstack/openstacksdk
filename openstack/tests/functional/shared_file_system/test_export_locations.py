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

from openstack.tests.functional.shared_file_system import base


class TestExportLocation(base.BaseSharedFileSystemTest):
    min_microversion = '2.9'

    def setUp(self):
        super().setUp()

        self.SHARE_NAME = self.getUniqueString()
        my_share = self.create_share(
            name=self.SHARE_NAME,
            size=2,
            share_type="dhss_false",
            share_protocol='NFS',
            description=None,
        )
        self.SHARE_ID = my_share.id

    def test_export_locations(self):
        exs = self.user_cloud.shared_file_system.export_locations(
            self.SHARE_ID
        )
        self.assertGreater(len(list(exs)), 0)
        for ex in exs:
            for attribute in (
                'id',
                'path',
                'share_instance_id',
                'updated_at',
                'created_at',
            ):
                self.assertTrue(hasattr(ex, attribute))
                self.assertIsInstance(getattr(ex, attribute), 'str')
            for attribute in ('is_preferred', 'is_admin'):
                self.assertTrue(hasattr(ex, attribute))
                self.assertIsInstance(getattr(ex, attribute), 'bool')
