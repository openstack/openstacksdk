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
from shade import meta
from shade.tests.unit import base


class TestVolumeBackups(base.RequestsMockTestCase):
    def test_search_volume_backups(self):
        name = 'Volume1'
        vol1 = {'name': name, 'availability_zone': 'az1'}
        vol2 = {'name': name, 'availability_zone': 'az1'}
        vol3 = {'name': 'Volume2', 'availability_zone': 'az2'}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['backups', 'detail']),
                 json={"backups": [vol1, vol2, vol3]})])
        result = self.cloud.search_volume_backups(
            name, {'availability_zone': 'az1'})
        self.assertEqual(len(result), 2)
        self.assertEqual(
            meta.obj_list_to_munch([vol1, vol2]),
            result)
        self.assert_calls()

    def test_get_volume_backup(self):
        name = 'Volume1'
        vol1 = {'name': name, 'availability_zone': 'az1'}
        vol2 = {'name': name, 'availability_zone': 'az2'}
        vol3 = {'name': 'Volume2', 'availability_zone': 'az1'}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['backups', 'detail']),
                 json={"backups": [vol1, vol2, vol3]})])
        result = self.cloud.get_volume_backup(
            name, {'availability_zone': 'az1'})
        result = meta.obj_to_munch(result)
        self.assertEqual(
            meta.obj_to_munch(vol1),
            result)
        self.assert_calls()

    def test_list_volume_backups(self):
        backup = {'id': '6ff16bdf-44d5-4bf9-b0f3-687549c76414',
                  'status': 'available'}
        search_opts = {'status': 'available'}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public', append=['backups', 'detail'],
                     qs_elements=['='.join(i) for i in search_opts.items()]),
                 json={"backups": [backup]})])
        result = self.cloud.list_volume_backups(True, search_opts)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            meta.obj_list_to_munch([backup]),
            result)
        self.assert_calls()

    def test_delete_volume_backup_wait(self):
        backup_id = '6ff16bdf-44d5-4bf9-b0f3-687549c76414'
        backup = {'id': backup_id}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', 'detail']),
                 json={"backups": [backup]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', backup_id])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', 'detail']),
                 json={"backups": [backup]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', 'detail']),
                 json={"backups": []})])
        self.cloud.delete_volume_backup(backup_id, False, True, 1)
        self.assert_calls()

    def test_delete_volume_backup_force(self):
        backup_id = '6ff16bdf-44d5-4bf9-b0f3-687549c76414'
        backup = {'id': backup_id}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', 'detail']),
                 json={"backups": [backup]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', backup_id, 'action']),
                 json={'os-force_delete': {}},
                 validate=dict(json={u'os-force_delete': None})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', 'detail']),
                 json={"backups": [backup]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['backups', 'detail']),
                 json={"backups": []})
        ])
        self.cloud.delete_volume_backup(backup_id, True, True, 1)
        self.assert_calls()
