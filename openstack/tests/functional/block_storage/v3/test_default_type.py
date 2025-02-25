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

from openstack.block_storage.v3 import default_type as _default_type
from openstack.tests.functional.block_storage.v3 import base


class TestDefaultType(base.BaseBlockStorageTest):
    def setUp(self):
        super().setUp()
        if not self._operator_cloud_name:
            self.skip("Operator cloud must be set for this test")
        self._set_operator_cloud(block_storage_api_version='3.67')
        self.PROJECT_ID = self.create_temporary_project().id

    def test_default_type(self):
        # Create a volume type
        type_name = self.getUniqueString()
        volume_type_id = self.operator_cloud.block_storage.create_type(
            name=type_name,
        ).id

        # Set default type for a project
        default_type = self.operator_cloud.block_storage.set_default_type(
            self.PROJECT_ID,
            volume_type_id,
        )
        self.assertIsInstance(default_type, _default_type.DefaultType)

        # Show default type for a project
        default_type = self.operator_cloud.block_storage.show_default_type(
            self.PROJECT_ID
        )
        self.assertIsInstance(default_type, _default_type.DefaultType)
        self.assertEqual(volume_type_id, default_type.volume_type_id)

        # List all default types
        default_types = self.operator_cloud.block_storage.default_types()
        for default_type in default_types:
            self.assertIsInstance(default_type, _default_type.DefaultType)
            # There could be existing default types set in the environment
            # Just verify that the default type we have set is correct
            if self.PROJECT_ID == default_type.project_id:
                self.assertEqual(volume_type_id, default_type.volume_type_id)

        # Unset default type for a project
        default_type = self.operator_cloud.block_storage.unset_default_type(
            self.PROJECT_ID
        )
        self.assertIsNone(default_type)

        # Delete the volume type
        vol_type = self.operator_cloud.block_storage.delete_type(
            volume_type_id,
            ignore_missing=False,
        )
        self.assertIsNone(vol_type)
