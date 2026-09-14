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

from fixtures import TimeoutException

from openstack import exceptions
from openstack.tests.functional import base
from openstack import utils
from testtools import content


class TestVolume(base.BaseFunctionalTest):
    # Creating and deleting volumes is slow
    TIMEOUT_SCALING_FACTOR = 2

    def setUp(self):
        super().setUp()
        self.skipTest('Volume functional tests temporarily disabled')
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')

    def test_volumes(self):
        '''Test volume and snapshot functionality'''
        volume_name = self.getUniqueString()
        snapshot_name = self.getUniqueString()
        self.addDetail('volume', content.text_content(volume_name))
        self.addCleanup(self.cleanup, volume_name, snapshot_name=snapshot_name)
        volume = self.user_cloud.create_volume(
            display_name=volume_name, size=1
        )
        snapshot = self.user_cloud.create_volume_snapshot(
            volume['id'], display_name=snapshot_name
        )

        ret_volume = self.user_cloud.get_volume_by_id(volume['id'])
        self.assertEqual(volume['id'], ret_volume['id'])

        volume_ids = [v['id'] for v in self.user_cloud.list_volumes()]
        self.assertIn(volume['id'], volume_ids)

        snapshot_list = self.user_cloud.list_volume_snapshots()
        snapshot_ids = [s['id'] for s in snapshot_list]
        self.assertIn(snapshot['id'], snapshot_ids)

        ret_snapshot = self.user_cloud.get_volume_snapshot_by_id(
            snapshot['id']
        )
        self.assertEqual(snapshot['id'], ret_snapshot['id'])

        self.user_cloud.delete_volume_snapshot(snapshot_name, wait=True)
        self.user_cloud.delete_volume(volume_name, wait=True)

    def test_volume_to_image(self):
        '''Test volume export to image functionality'''
        volume_name = self.getUniqueString()
        image_name = self.getUniqueString()
        self.addDetail('volume', content.text_content(volume_name))
        self.addCleanup(self.cleanup, volume_name, image_name=image_name)
        volume = self.user_cloud.create_volume(
            display_name=volume_name, size=1
        )
        image = self.user_cloud.create_image(
            image_name, volume=volume, wait=True
        )
        assert image is not None

        volume_ids = [v['id'] for v in self.user_cloud.list_volumes()]
        self.assertIn(volume['id'], volume_ids)

        image_list = self.user_cloud.list_images()
        image_ids = [s['id'] for s in image_list]
        self.assertIn(image['id'], image_ids)

        self.user_cloud.delete_image(image_name, wait=True)
        self.user_cloud.delete_volume(volume_name, wait=True)

    def cleanup(self, volume, snapshot_name=None, image_name=None):
        # Need to delete snapshots before volumes
        if snapshot_name:
            snapshot = self.user_cloud.get_volume_snapshot(snapshot_name)
            if snapshot:
                self.user_cloud.delete_volume_snapshot(
                    snapshot_name, wait=True
                )
        if image_name:
            image = self.user_cloud.get_image(image_name)
            if image:
                self.user_cloud.delete_image(image_name, wait=True)
        if not isinstance(volume, list):
            self.user_cloud.delete_volume(volume, wait=True)
        else:
            # We have more than one volume to clean up - submit all of the
            # deletes without wait, then poll until none of them are found
            # in the volume list anymore
            for v in volume:
                self.user_cloud.delete_volume(v, wait=False)
            try:
                for count in utils.iterate_timeout(
                    180, "Timeout waiting for volume cleanup"
                ):
                    found = False
                    for existing in self.user_cloud.list_volumes():
                        for v in volume:
                            if v['id'] == existing['id']:
                                found = True
                                break
                        if found:
                            break
                    if not found:
                        break
            except (exceptions.ResourceTimeout, TimeoutException):
                # NOTE(slaweq): ups, some volumes are still not removed
                # so we should try to force delete it once again and move
                # forward
                for existing in self.user_cloud.list_volumes():
                    for v in volume:
                        if v['id'] == existing['id']:
                            self.operator_cloud.delete_volume(
                                v, wait=False, force=True
                            )

    def test_list_volumes_pagination(self):
        '''Test pagination for list volumes functionality'''

        volumes = []
        # the number of created volumes needs to be higher than
        # CONF.osapi_max_limit but not higher than volume quotas for
        # the test user in the tenant(default quotas is set to 10)
        num_volumes = 8
        for i in range(num_volumes):
            name = self.getUniqueString()
            v = self.user_cloud.create_volume(display_name=name, size=1)
            volumes.append(v)
        self.addCleanup(self.cleanup, volumes)
        result = []
        for v in self.user_cloud.list_volumes():
            if v['name'] and v['name'].startswith(self.id()):
                result.append(v['id'])
        self.assertEqual(sorted([v['id'] for v in volumes]), sorted(result))

    def test_update_volume(self):
        name, desc = self.getUniqueString('name'), self.getUniqueString('desc')
        self.addCleanup(self.cleanup, name)
        volume = self.user_cloud.create_volume(1, name=name, description=desc)
        self.assertEqual(volume.name, name)
        self.assertEqual(volume.description, desc)
        new_name = self.getUniqueString('name')
        volume = self.user_cloud.update_volume(volume.id, name=new_name)
        self.assertNotEqual(volume.name, name)
        self.assertEqual(volume.name, new_name)
        self.assertEqual(volume.description, desc)


class TestVolumeBackup(base.BaseFunctionalTest):
    # Creating a volume backup is incredibly slow.
    TIMEOUT_SCALING_FACTOR = 2

    def setUp(self):
        super().setUp()
        self.skipTest('Volume functional tests temporarily disabled')
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')

        if not self.user_cloud.has_service('object-store'):
            self.skipTest('volume backups require swift')

    def test_create_get_delete_volume_backup(self):
        volume = self.user_cloud.create_volume(
            display_name=self.getUniqueString(), size=1
        )
        self.addCleanup(self.user_cloud.delete_volume, volume['id'])

        backup_name_1 = self.getUniqueString()
        backup_desc_1 = self.getUniqueString()
        backup = self.user_cloud.create_volume_backup(
            volume_id=volume['id'],
            name=backup_name_1,
            description=backup_desc_1,
            wait=True,
        )
        self.assertEqual(backup_name_1, backup['name'])

        fetched_backup = self.user_cloud.get_volume_backup(backup['id'])
        assert fetched_backup is not None
        backup = fetched_backup
        self.assertEqual("available", backup['status'])
        self.assertEqual(backup_desc_1, backup['description'])

        self.user_cloud.delete_volume_backup(backup['id'], wait=True)
        self.assertIsNone(self.user_cloud.get_volume_backup(backup['id']))

    def test_create_get_delete_volume_backup_from_snapshot(self):
        volume = self.user_cloud.create_volume(size=1)
        snapshot = self.user_cloud.create_volume_snapshot(volume['id'])
        self.addCleanup(self.user_cloud.delete_volume, volume['id'])
        self.addCleanup(
            self.user_cloud.delete_volume_snapshot, snapshot['id'], wait=True
        )

        backup = self.user_cloud.create_volume_backup(
            volume_id=volume['id'], snapshot_id=snapshot['id'], wait=True
        )

        fetched_backup = self.user_cloud.get_volume_backup(backup['id'])
        assert fetched_backup is not None
        backup = fetched_backup
        self.assertEqual(backup['snapshot_id'], snapshot['id'])

        self.user_cloud.delete_volume_backup(backup['id'], wait=True)
        self.assertIsNone(self.user_cloud.get_volume_backup(backup['id']))

    def test_create_get_delete_incremental_volume_backup(self):
        volume = self.user_cloud.create_volume(size=1)
        self.addCleanup(self.user_cloud.delete_volume, volume['id'])

        full_backup = self.user_cloud.create_volume_backup(
            volume_id=volume['id'], wait=True
        )
        incr_backup = self.user_cloud.create_volume_backup(
            volume_id=volume['id'], incremental=True, wait=True
        )

        fetched_full_backup = self.user_cloud.get_volume_backup(
            full_backup['id']
        )
        fetched_incr_backup = self.user_cloud.get_volume_backup(
            incr_backup['id']
        )
        assert fetched_full_backup is not None
        assert fetched_incr_backup is not None
        full_backup = fetched_full_backup
        incr_backup = fetched_incr_backup
        self.assertEqual(full_backup['has_dependent_backups'], True)
        self.assertEqual(incr_backup['is_incremental'], True)

        self.user_cloud.delete_volume_backup(incr_backup['id'], wait=True)
        self.user_cloud.delete_volume_backup(full_backup['id'], wait=True)
        self.assertIsNone(self.user_cloud.get_volume_backup(full_backup['id']))
        self.assertIsNone(self.user_cloud.get_volume_backup(incr_backup['id']))

    def test_list_volume_backups(self):
        vol1 = self.user_cloud.create_volume(
            display_name=self.getUniqueString(), size=1
        )
        self.addCleanup(self.user_cloud.delete_volume, vol1['id'])

        # We create 2 volumes to create 2 backups. We could have created 2
        # backups from the same volume but taking 2 successive backups seems
        # to be race-condition prone. And I didn't want to use an ugly sleep()
        # here.
        vol2 = self.user_cloud.create_volume(
            display_name=self.getUniqueString(), size=1
        )
        self.addCleanup(self.user_cloud.delete_volume, vol2['id'])

        backup_name_1 = self.getUniqueString()
        backup = self.user_cloud.create_volume_backup(
            volume_id=vol1['id'], name=backup_name_1
        )
        self.addCleanup(self.user_cloud.delete_volume_backup, backup['id'])

        backup = self.user_cloud.create_volume_backup(volume_id=vol2['id'])
        self.addCleanup(self.user_cloud.delete_volume_backup, backup['id'])

        backups = self.user_cloud.list_volume_backups()
        self.assertEqual(2, len(backups))

        backups = self.user_cloud.list_volume_backups(
            filters={"name": backup_name_1}
        )
        self.assertEqual(1, len(backups))
        self.assertEqual(backup_name_1, backups[0]['name'])


class TestVolumeType(base.BaseFunctionalTest):
    def _assert_project(self, volume_name_or_id, project_id, allowed=True):
        acls = self.operator_cloud.get_volume_type_access(volume_name_or_id)
        allowed_projects = [x.get('project_id') for x in acls]
        self.assertEqual(allowed, project_id in allowed_projects)

    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')
        volume_type = {
            "name": 'test-volume-type',
            "description": None,
            "os-volume-type-access:is_public": False,
        }
        self.operator_cloud.block_storage.post(
            '/types', json={'volume_type': volume_type}
        )

    def tearDown(self):
        ret = self.operator_cloud.get_volume_type('test-volume-type')
        if ret is not None and ret.get('id'):
            self.operator_cloud.block_storage.delete(f'/types/{ret.id}')
        super().tearDown()

    def test_list_volume_types(self):
        volume_types = self.operator_cloud.list_volume_types()
        self.assertTrue(volume_types)
        self.assertTrue(
            any(x for x in volume_types if x.name == 'test-volume-type')
        )

    def test_add_remove_volume_type_access(self):
        volume_type = self.operator_cloud.get_volume_type('test-volume-type')
        assert volume_type is not None
        self.assertEqual('test-volume-type', volume_type.name)

        project_id = self.operator_cloud.current_project_id
        assert project_id is not None

        self.operator_cloud.add_volume_type_access(
            'test-volume-type', project_id
        )
        self._assert_project(
            'test-volume-type',
            project_id,
            allowed=True,
        )

        self.operator_cloud.remove_volume_type_access(
            'test-volume-type', project_id
        )
        self._assert_project(
            'test-volume-type',
            project_id,
            allowed=False,
        )

    def test_add_volume_type_access_missing_project(self):
        # Project id is not valitaded and it may not exist.
        self.operator_cloud.add_volume_type_access(
            'test-volume-type', '00000000000000000000000000000000'
        )

        self.operator_cloud.remove_volume_type_access(
            'test-volume-type', '00000000000000000000000000000000'
        )

    def test_add_volume_type_access_missing_volume(self):
        project_id = self.operator_cloud.current_project_id
        assert project_id is not None
        with self.assertRaises(
            exceptions.SDKException, msg="VolumeType not found.*"
        ):
            self.operator_cloud.add_volume_type_access(
                'MISSING_VOLUME_TYPE', project_id
            )

    def test_remove_volume_type_access_missing_volume(self):
        project_id = self.operator_cloud.current_project_id
        assert project_id is not None
        with self.assertRaises(
            exceptions.SDKException, msg="VolumeType not found.*"
        ):
            self.operator_cloud.remove_volume_type_access(
                'MISSING_VOLUME_TYPE', project_id
            )

    def test_add_volume_type_access_bad_project(self):
        with self.assertRaises(
            exceptions.BadRequestException, msg="Unable to authorize.*"
        ):
            self.operator_cloud.add_volume_type_access(
                'test-volume-type', 'BAD_PROJECT_ID'
            )

    def test_remove_volume_type_access_missing_project(self):
        with self.assertRaises(
            exceptions.NotFoundException, msg="Unable to revoke.*"
        ):
            self.operator_cloud.remove_volume_type_access(
                'test-volume-type', '00000000000000000000000000000000'
            )


class TestVolumeLimits(base.BaseFunctionalTest):
    def test_get_our_volume_limits(self):
        """Test limits functionality"""
        limits = self.user_cloud.get_volume_limits()
        self.assertIsNotNone(limits)
        self.assertFalse(hasattr(limits, 'maxTotalVolumes'))

    def test_get_other_volume_limits(self):
        """Test limits functionality"""
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        limits = self.operator_cloud.get_volume_limits('demo')
        self.assertFalse(hasattr(limits, 'maxTotalVolumes'))


class TestVolumeQuotas(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.user_cloud.has_service('volume'):
            self.skipTest('volume service not supported by cloud')

    def test_get_quotas(self):
        '''Test get quotas functionality'''
        project_id = self.user_cloud.current_project_id
        assert project_id is not None
        self.user_cloud.get_volume_quotas(project_id)

    def test_set_quotas(self):
        '''Test set quotas functionality'''
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        quotas = self.operator_cloud.get_volume_quotas('demo')
        volumes = quotas['volumes']
        self.operator_cloud.set_volume_quotas('demo', volumes=volumes + 1)
        self.assertEqual(
            volumes + 1,
            self.operator_cloud.get_volume_quotas('demo')['volumes'],
        )
        self.operator_cloud.delete_volume_quotas('demo')
        self.assertEqual(
            volumes, self.operator_cloud.get_volume_quotas('demo')['volumes']
        )
