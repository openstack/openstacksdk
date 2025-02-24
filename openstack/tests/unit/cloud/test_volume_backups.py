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
from openstack.block_storage.v3 import backup
from openstack.tests.unit import base


class TestVolumeBackups(base.TestCase):
    def setUp(self):
        super().setUp()
        self.use_cinder()

    def _compare_backups(self, exp, real):
        self.assertDictEqual(
            backup.Backup(**exp).to_dict(computed=False),
            real.to_dict(computed=False),
        )

    def test_search_volume_backups(self):
        name = 'Volume1'
        vol1 = {'name': name, 'availability_zone': 'az1'}
        vol2 = {'name': name, 'availability_zone': 'az1'}
        vol3 = {'name': 'Volume2', 'availability_zone': 'az2'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', 'detail']
                    ),
                    json={"backups": [vol1, vol2, vol3]},
                )
            ]
        )
        result = self.cloud.search_volume_backups(
            name, {'availability_zone': 'az1'}
        )
        self.assertEqual(len(result), 2)
        for a, b in zip([vol1, vol2], result):
            self._compare_backups(a, b)
        self.assert_calls()

    def test_get_volume_backup(self):
        name = 'Volume1'
        backup = {'name': name, 'availability_zone': 'az1'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', name]
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['backups', 'detail'],
                        qs_elements=[f'name={name}'],
                    ),
                    json={"backups": [backup]},
                ),
            ]
        )
        result = self.cloud.get_volume_backup(name)
        self._compare_backups(backup, result)
        self.assert_calls()

    def test_get_volume_backup_with_filters(self):
        name = 'Volume1'
        vol1 = {'name': name, 'availability_zone': 'az1'}
        vol2 = {'name': name, 'availability_zone': 'az2'}
        vol3 = {'name': 'Volume2', 'availability_zone': 'az1'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', 'detail']
                    ),
                    json={"backups": [vol1, vol2, vol3]},
                )
            ]
        )
        result = self.cloud.get_volume_backup(
            name, {'availability_zone': 'az1'}
        )
        self._compare_backups(vol1, result)
        self.assert_calls()

    def test_list_volume_backups(self):
        backup = {
            'id': '6ff16bdf-44d5-4bf9-b0f3-687549c76414',
            'status': 'available',
        }
        search_opts = {'status': 'available'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['backups', 'detail'],
                        qs_elements=['='.join(i) for i in search_opts.items()],
                    ),
                    json={"backups": [backup]},
                )
            ]
        )
        result = self.cloud.list_volume_backups(True, search_opts)
        self.assertEqual(len(result), 1)

        self._compare_backups(backup, result[0])
        self.assert_calls()

    def test_delete_volume_backup_wait(self):
        backup_id = '6ff16bdf-44d5-4bf9-b0f3-687549c76414'
        backup = {'id': backup_id, 'status': 'available'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', backup_id]
                    ),
                    json={'backup': backup},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', backup_id]
                    ),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', backup_id]
                    ),
                    json={"backup": backup},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', backup_id]
                    ),
                    status_code=404,
                ),
            ]
        )
        self.cloud.delete_volume_backup(backup_id, False, True, 1)
        self.assert_calls()

    def test_delete_volume_backup_force(self):
        backup_id = '6ff16bdf-44d5-4bf9-b0f3-687549c76414'
        backup = {'id': backup_id, 'status': 'available'}
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', backup_id]
                    ),
                    json={'backup': backup},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3',
                        'public',
                        append=['backups', backup_id, 'action'],
                    ),
                    json={'os-force_delete': None},
                    validate=dict(json={'os-force_delete': None}),
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', backup_id]
                    ),
                    json={"backup": backup},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups', backup_id]
                    ),
                    status_code=404,
                ),
            ]
        )
        self.cloud.delete_volume_backup(backup_id, True, True, 1)
        self.assert_calls()

    def test_create_volume_backup(self):
        volume_id = '1234'
        backup_name = 'bak1'
        bak1 = {
            'id': '5678',
            'volume_id': volume_id,
            'status': 'available',
            'name': backup_name,
        }

        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups']
                    ),
                    json={'backup': bak1},
                    validate=dict(
                        json={
                            'backup': {
                                'name': backup_name,
                                'volume_id': volume_id,
                                'description': None,
                                'force': False,
                                'snapshot_id': None,
                                'incremental': False,
                            }
                        }
                    ),
                ),
            ]
        )
        self.cloud.create_volume_backup(volume_id, name=backup_name)
        self.assert_calls()

    def test_create_incremental_volume_backup(self):
        volume_id = '1234'
        backup_name = 'bak1'
        bak1 = {
            'id': '5678',
            'volume_id': volume_id,
            'status': 'available',
            'name': backup_name,
        }

        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups']
                    ),
                    json={'backup': bak1},
                    validate=dict(
                        json={
                            'backup': {
                                'name': backup_name,
                                'volume_id': volume_id,
                                'description': None,
                                'force': False,
                                'snapshot_id': None,
                                'incremental': True,
                            }
                        }
                    ),
                ),
            ]
        )
        self.cloud.create_volume_backup(
            volume_id, name=backup_name, incremental=True
        )
        self.assert_calls()

    def test_create_volume_backup_from_snapshot(self):
        volume_id = '1234'
        backup_name = 'bak1'
        snapshot_id = '5678'
        bak1 = {
            'id': '5678',
            'volume_id': volume_id,
            'status': 'available',
            'name': 'bak1',
        }

        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'volumev3', 'public', append=['backups']
                    ),
                    json={'backup': bak1},
                    validate=dict(
                        json={
                            'backup': {
                                'name': backup_name,
                                'volume_id': volume_id,
                                'description': None,
                                'force': False,
                                'snapshot_id': snapshot_id,
                                'incremental': False,
                            }
                        }
                    ),
                ),
            ]
        )
        self.cloud.create_volume_backup(
            volume_id, name=backup_name, snapshot_id=snapshot_id
        )
        self.assert_calls()
