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
import mock

import shade
from shade.tests.unit import base


class TestVolumeBackups(base.TestCase):
    @mock.patch.object(shade.OpenStackCloud, 'list_volume_backups')
    @mock.patch("shade._utils._filter_list")
    def test_search_volume_backups(self, m_filter_list, m_list_volume_backups):
        result = self.cloud.search_volume_backups(
            mock.sentinel.name_or_id, mock.sentinel.filter)

        m_list_volume_backups.assert_called_once_with()
        m_filter_list.assert_called_once_with(
            m_list_volume_backups.return_value, mock.sentinel.name_or_id,
            mock.sentinel.filter)
        self.assertIs(m_filter_list.return_value, result)

    @mock.patch("shade._utils._get_entity")
    def test_get_volume_backup(self, m_get_entity):
        result = self.cloud.get_volume_backup(
            mock.sentinel.name_or_id, mock.sentinel.filter)

        self.assertIs(m_get_entity.return_value, result)
        m_get_entity.assert_called_once_with(
            self.cloud.search_volume_backups, mock.sentinel.name_or_id,
            mock.sentinel.filter)

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_list_volume_backups(self, m_cinder_client):
        backup_id = '6ff16bdf-44d5-4bf9-b0f3-687549c76414'
        m_cinder_client.backups.list.return_value = [
            {'id': backup_id}
        ]
        result = self.cloud.list_volume_backups(
            mock.sentinel.detailed, mock.sentinel.search_opts)

        m_cinder_client.backups.list.assert_called_once_with(
            detailed=mock.sentinel.detailed,
            search_opts=mock.sentinel.search_opts)
        self.assertEqual(backup_id, result[0]['id'])

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    @mock.patch("shade._utils._iterate_timeout")
    @mock.patch.object(shade.OpenStackCloud, 'get_volume_backup')
    def test_delete_volume_backup(self, m_get_volume_backup,
                                  m_iterate_timeout, m_cinder_client):
        m_get_volume_backup.side_effect = [{'id': 42}, True, False]
        self.cloud.delete_volume_backup(
            mock.sentinel.name_or_id, mock.sentinel.force, mock.sentinel.wait,
            mock.sentinel.timeout)

        m_iterate_timeout.assert_called_once_with(
            mock.sentinel.timeout, mock.ANY)
        m_cinder_client.backups.delete.assert_called_once_with(
            backup=42, force=mock.sentinel.force)

        # We expect 3 calls, the last return_value is False which breaks the
        # wait loop.
        m_get_volume_backup.call_args_list = [mock.call(42)] * 3
