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

"""
test_volume
----------------------------------

Functional tests for block storage methods.
"""

from fixtures import TimeoutException
from testtools import content

from openstack import exceptions
from openstack.tests.functional import base
from openstack import utils


class TestVolume(base.BaseFunctionalTest):
    # Creating and deleting volumes is slow
    TIMEOUT_SCALING_FACTOR = 1.5

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
