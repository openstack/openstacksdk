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

from openstack.shared_file_system.v2 import share_type as _share_type
from openstack.tests.functional.shared_file_system.v2 import base


class ShareTypeTest(base.BaseSharedFileSystemTest):
    def setUp(self):
        super().setUp()

        self.SHARE_TYPE_NAME = self.getUniqueString()
        stype = self.create_share_type(
            self.SHARE_TYPE_NAME,
            extra_specs={
                'driver_handles_share_servers': False,
                'snapshot_support': True,
                'delete': True,
            },
            description=None,
        )
        self.assertIsNotNone(stype)
        self.assertIsNotNone(stype.id)
        self.SHARE_TYPE_ID = stype.id

    def test_get_share_type(self):
        sot = self.operator_cloud.shared_file_system.get_share_type(
            self.SHARE_TYPE_ID
        )
        assert isinstance(sot, _share_type.ShareType)
        self.assertEqual(self.SHARE_TYPE_ID, sot.id)
        self.assertEqual(
            {
                'driver_handles_share_servers': 'False',
                'snapshot_support': 'True',
                'delete': 'True',
            },
            sot.extra_specs,
        )

    def test_list_share_type(self):
        share_types = self.user_cloud.shared_file_system.share_types()
        self.assertGreater(len(list(share_types)), 0)
        for share_type in share_types:
            for attribute in ('id', 'name', 'is_default', 'description'):
                self.assertTrue(hasattr(share_type, attribute))

    def test_delete_share_type(self):
        sot = self.operator_cloud.shared_file_system.delete_share_type(
            self.SHARE_TYPE_ID
        )
        self.assertIsNone(sot)

    def test_update_share_type(self):
        u_type = self.operator_cloud.shared_file_system.update_share_type(
            self.SHARE_TYPE_ID, description='updated share type'
        )
        get_u_type = self.operator_cloud.shared_file_system.get_share_type(
            u_type.id
        )
        self.assertEqual('updated share type', get_u_type.description)

    def test_update_share_type_extra_specs(self):
        sot = self.operator_cloud.shared_file_system.get_share_type(
            self.SHARE_TYPE_ID
        )
        sot_set = self.operator_cloud.shared_file_system.update_share_type_extra_specs(  # noqa: E501
            sot['id'], foo='bar', baz='qux'
        )

        expected_extra_specs = {
            'foo': 'bar',
            'baz': 'qux',
        }
        self.assertEqual(expected_extra_specs, sot_set['extra_specs'])
        self.assertIn('extra_specs', sot_set)

    def test_delete_share_type_extra_spec_property(self):
        sot = self.operator_cloud.shared_file_system.get_share_type(
            self.SHARE_TYPE_ID
        )
        self.operator_cloud.shared_file_system.delete_share_type_extra_spec_property(
            sot['id'], 'delete'
        )
        expected_extra_specs = {
            'driver_handles_share_servers': 'False',
            'snapshot_support': 'True',
        }
        sot = self.operator_cloud.shared_file_system.get_share_type(
            self.SHARE_TYPE_ID
        )
        self.assertEqual(expected_extra_specs, sot.extra_specs)
