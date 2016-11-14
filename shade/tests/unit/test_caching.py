# -*- coding: utf-8 -*-

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
import concurrent
import tempfile
import time

from glanceclient.v2 import shell
import mock
import os_client_config as occ
import testtools
import warlock

import shade.openstackcloud
from shade import _utils
from shade import exc
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


# Mock out the gettext function so that the task schema can be copypasta
def _(msg):
    return msg


_TASK_PROPERTIES = {
    "id": {
        "description": _("An identifier for the task"),
        "pattern": _('^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}'
                     '-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$'),
        "type": "string"
    },
    "type": {
        "description": _("The type of task represented by this content"),
        "enum": [
            "import",
        ],
        "type": "string"
    },
    "status": {
        "description": _("The current status of this task"),
        "enum": [
            "pending",
            "processing",
            "success",
            "failure"
        ],
        "type": "string"
    },
    "input": {
        "description": _("The parameters required by task, JSON blob"),
        "type": ["null", "object"],
    },
    "result": {
        "description": _("The result of current task, JSON blob"),
        "type": ["null", "object"],
    },
    "owner": {
        "description": _("An identifier for the owner of this task"),
        "type": "string"
    },
    "message": {
        "description": _("Human-readable informative message only included"
                         " when appropriate (usually on failure)"),
        "type": "string",
    },
    "expires_at": {
        "description": _("Datetime when this resource would be"
                         " subject to removal"),
        "type": ["null", "string"]
    },
    "created_at": {
        "description": _("Datetime when this resource was created"),
        "type": "string"
    },
    "updated_at": {
        "description": _("Datetime when this resource was updated"),
        "type": "string"
    },
    'self': {'type': 'string'},
    'schema': {'type': 'string'}
}
_TASK_SCHEMA = dict(
    name='Task', properties=_TASK_PROPERTIES,
    additionalProperties=False,
)


class TestMemoryCache(base.TestCase):

    def setUp(self):
        super(TestMemoryCache, self).setUp(
            cloud_config_fixture='clouds_cache.yaml')

    def _image_dict(self, fake_image):
        return self.cloud._normalize_image(meta.obj_to_dict(fake_image))

    def test_openstack_cloud(self):
        self.assertIsInstance(self.cloud, shade.OpenStackCloud)

    @mock.patch('shade.OpenStackCloud.keystone_client')
    def test_list_projects_v3(self, keystone_mock):
        project = fakes.FakeProject('project_a')
        keystone_mock.projects.list.return_value = [project]
        self.cloud.cloud_config.config['identity_api_version'] = '3'
        self.assertEqual(
            self.cloud._normalize_projects(meta.obj_list_to_dict([project])),
            self.cloud.list_projects())
        project_b = fakes.FakeProject('project_b')
        keystone_mock.projects.list.return_value = [project, project_b]
        self.assertEqual(
            self.cloud._normalize_projects(meta.obj_list_to_dict([project])),
            self.cloud.list_projects())
        self.cloud.list_projects.invalidate(self.cloud)
        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict([project, project_b])),
            self.cloud.list_projects())

    @mock.patch('shade.OpenStackCloud.keystone_client')
    def test_list_projects_v2(self, keystone_mock):
        project = fakes.FakeProject('project_a')
        keystone_mock.tenants.list.return_value = [project]
        self.cloud.cloud_config.config['identity_api_version'] = '2'
        self.assertEqual(
            self.cloud._normalize_projects(meta.obj_list_to_dict([project])),
            self.cloud.list_projects())
        project_b = fakes.FakeProject('project_b')
        keystone_mock.tenants.list.return_value = [project, project_b]
        self.assertEqual(
            self.cloud._normalize_projects(meta.obj_list_to_dict([project])),
            self.cloud.list_projects())
        self.cloud.list_projects.invalidate(self.cloud)
        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict([project, project_b])),
            self.cloud.list_projects())

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_list_servers_herd(self, nova_mock):
        self.cloud._SERVER_AGE = 0
        fake_server = fakes.FakeServer('1234', '', 'ACTIVE')
        nova_mock.servers.list.return_value = [fake_server]
        with concurrent.futures.ThreadPoolExecutor(16) as pool:
            for i in range(16):
                pool.submit(lambda: self.cloud.list_servers())
                # It's possible to race-condition 16 threads all in the
                # single initial lock without a tiny sleep
                time.sleep(0.001)
        self.assertGreater(nova_mock.servers.list.call_count, 1)

    @mock.patch('shade.OpenStackCloud.nova_client')
    def test_list_servers_no_herd(self, nova_mock):
        self.cloud._SERVER_AGE = 2
        fake_server = fakes.FakeServer('1234', '', 'ACTIVE')
        nova_mock.servers.list.return_value = [fake_server]
        with concurrent.futures.ThreadPoolExecutor(16) as pool:
            for i in range(16):
                pool.submit(lambda: self.cloud.list_servers())
                # It's possible to race-condition 16 threads all in the
                # single initial lock without a tiny sleep
                time.sleep(0.001)
        self.assertEqual(1, nova_mock.servers.list.call_count)

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes(self, cinder_mock):
        fake_volume = fakes.FakeVolume('volume1', 'available',
                                       'Volume 1 Display Name')
        fake_volume_dict = _utils.normalize_volumes(
            [meta.obj_to_dict(fake_volume)])[0]
        cinder_mock.volumes.list.return_value = [fake_volume]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        fake_volume2 = fakes.FakeVolume('volume2', 'available',
                                        'Volume 2 Display Name')
        fake_volume2_dict = _utils.normalize_volumes(
            [meta.obj_to_dict(fake_volume2)])[0]
        cinder_mock.volumes.list.return_value = [fake_volume, fake_volume2]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        self.cloud.list_volumes.invalidate(self.cloud)
        self.assertEqual([fake_volume_dict, fake_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes_creating_invalidates(self, cinder_mock):
        fake_volume = fakes.FakeVolume('volume1', 'creating',
                                       'Volume 1 Display Name')
        fake_volume_dict = _utils.normalize_volumes(
            [meta.obj_to_dict(fake_volume)])[0]
        cinder_mock.volumes.list.return_value = [fake_volume]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        fake_volume2 = fakes.FakeVolume('volume2', 'available',
                                        'Volume 2 Display Name')
        fake_volume2_dict = _utils.normalize_volumes(
            [meta.obj_to_dict(fake_volume2)])[0]
        cinder_mock.volumes.list.return_value = [fake_volume, fake_volume2]
        self.assertEqual([fake_volume_dict, fake_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_create_volume_invalidates(self, cinder_mock):
        fake_volb4 = fakes.FakeVolume('volume1', 'available',
                                      'Volume 1 Display Name')
        fake_volb4_dict = _utils.normalize_volumes(
            [meta.obj_to_dict(fake_volb4)])[0]
        cinder_mock.volumes.list.return_value = [fake_volb4]
        self.assertEqual([fake_volb4_dict], self.cloud.list_volumes())
        volume = dict(display_name='junk_vol',
                      size=1,
                      display_description='test junk volume')
        fake_vol = fakes.FakeVolume('12345', 'creating', '')
        fake_vol_dict = meta.obj_to_dict(fake_vol)
        fake_vol_dict = _utils.normalize_volumes(
            [meta.obj_to_dict(fake_vol)])[0]
        cinder_mock.volumes.create.return_value = fake_vol
        cinder_mock.volumes.list.return_value = [fake_volb4, fake_vol]

        def creating_available():
            def now_available():
                fake_vol.status = 'available'
                fake_vol_dict['status'] = 'available'
                return mock.DEFAULT
            cinder_mock.volumes.list.side_effect = now_available
            return mock.DEFAULT
        cinder_mock.volumes.list.side_effect = creating_available
        self.cloud.create_volume(wait=True, timeout=None, **volume)
        self.assertTrue(cinder_mock.volumes.create.called)
        self.assertEqual(3, cinder_mock.volumes.list.call_count)
        # If cache was not invalidated, we would not see our own volume here
        # because the first volume was available and thus would already be
        # cached.
        self.assertEqual([fake_volb4_dict, fake_vol_dict],
                         self.cloud.list_volumes())

        # And now delete and check same thing since list is cached as all
        # available
        fake_vol.status = 'deleting'
        fake_vol_dict = meta.obj_to_dict(fake_vol)

        def deleting_gone():
            def now_gone():
                cinder_mock.volumes.list.return_value = [fake_volb4]
                return mock.DEFAULT
            cinder_mock.volumes.list.side_effect = now_gone
            return mock.DEFAULT
        cinder_mock.volumes.list.return_value = [fake_volb4, fake_vol]
        cinder_mock.volumes.list.side_effect = deleting_gone
        cinder_mock.volumes.delete.return_value = fake_vol_dict
        self.cloud.delete_volume('12345')
        self.assertEqual([fake_volb4_dict], self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_users(self, keystone_mock):
        fake_user = fakes.FakeUser('999', '', '')
        keystone_mock.users.list.return_value = [fake_user]
        users = self.cloud.list_users()
        self.assertEqual(1, len(users))
        self.assertEqual('999', users[0]['id'])
        self.assertEqual('', users[0]['name'])
        self.assertEqual('', users[0]['email'])

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_modify_user_invalidates_cache(self, keystone_mock):
        fake_user = fakes.FakeUser('abc123', 'abc123@domain.test',
                                   'abc123 name')
        # first cache an empty list
        keystone_mock.users.list.return_value = []
        self.assertEqual([], self.cloud.list_users())
        # now add one
        keystone_mock.users.list.return_value = [fake_user]
        keystone_mock.users.create.return_value = fake_user
        created = self.cloud.create_user(name='abc123 name',
                                         email='abc123@domain.test')
        self.assertEqual('abc123', created['id'])
        self.assertEqual('abc123 name', created['name'])
        self.assertEqual('abc123@domain.test', created['email'])

        # Cache should have been invalidated
        users = self.cloud.list_users()
        self.assertEqual(1, len(users))
        self.assertEqual('abc123', users[0]['id'])
        self.assertEqual('abc123 name', users[0]['name'])
        self.assertEqual('abc123@domain.test', users[0]['email'])

        # Update and check to see if it is updated
        fake_user2 = fakes.FakeUser('abc123',
                                    'abc123-changed@domain.test',
                                    'abc123 name')
        fake_user2_dict = meta.obj_to_dict(fake_user2)
        keystone_mock.users.update.return_value = fake_user2
        keystone_mock.users.list.return_value = [fake_user2]
        keystone_mock.users.get.return_value = fake_user2_dict
        self.cloud.update_user('abc123', email='abc123-changed@domain.test')
        keystone_mock.users.update.assert_called_with(
            user=fake_user2_dict, email='abc123-changed@domain.test')
        users = self.cloud.list_users()
        self.assertEqual(1, len(users))
        self.assertEqual('abc123', users[0]['id'])
        self.assertEqual('abc123 name', users[0]['name'])
        self.assertEqual('abc123-changed@domain.test', users[0]['email'])
        # Now delete and ensure it disappears
        keystone_mock.users.list.return_value = []
        self.cloud.delete_user('abc123')
        self.assertEqual([], self.cloud.list_users())
        self.assertTrue(keystone_mock.users.delete.was_called)

    @mock.patch.object(shade.OpenStackCloud, '_compute_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_flavors(self, nova_mock, mock_compute):
        nova_mock.flavors.list.return_value = []
        nova_mock.flavors.api.client.get.return_value = {}
        mock_response = mock.Mock()
        mock_response.json.return_value = dict(extra_specs={})
        mock_response.headers.get.return_value = 'request-id'
        mock_compute.get.return_value = mock_response
        self.assertEqual([], self.cloud.list_flavors())

        fake_flavor = fakes.FakeFlavor('555', 'vanilla', 100)
        fake_flavor_dict = self.cloud._normalize_flavor(
            meta.obj_to_dict(fake_flavor))
        nova_mock.flavors.list.return_value = [fake_flavor]
        self.cloud.list_flavors.invalidate(self.cloud)
        self.assertEqual([fake_flavor_dict], self.cloud.list_flavors())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images(self, glance_mock):
        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('22', '22 name', 'success')
        fake_image_dict = self._image_dict(fake_image)
        glance_mock.images.list.return_value = [fake_image]
        self.cloud.list_images.invalidate(self.cloud)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images_ignores_unsteady_status(self, glance_mock):
        steady_image = fakes.FakeImage('68', 'Jagr', 'active')
        steady_image_dict = self._image_dict(steady_image)
        for status in ('queued', 'saving', 'pending_delete'):
            active_image = fakes.FakeImage(self.getUniqueString(),
                                           self.getUniqueString(), status)
            glance_mock.images.list.return_value = [active_image]
            active_image_dict = self._image_dict(active_image)

            self.assertEqual([active_image_dict], self.cloud.list_images())
            glance_mock.images.list.return_value = [active_image, steady_image]
            # Should expect steady_image to appear if active wasn't cached
            self.assertEqual([active_image_dict, steady_image_dict],
                             self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_list_images_caches_steady_status(self, glance_mock):
        steady_image = fakes.FakeImage('91', 'Federov', 'active')
        first_image = None
        for status in ('active', 'deleted', 'killed'):
            active_image = fakes.FakeImage(self.getUniqueString(),
                                           self.getUniqueString(), status)
            active_image_dict = self._image_dict(active_image)
            if not first_image:
                first_image = active_image_dict
            glance_mock.images.list.return_value = [active_image]
            self.assertEqual([first_image], self.cloud.list_images())
            glance_mock.images.list.return_value = [active_image, steady_image]
            # because we skipped the create_image code path, no invalidation
            # was done, so we _SHOULD_ expect steady state images to cache and
            # therefore we should _not_ expect to see the new one here
            self.assertEqual([first_image], self.cloud.list_images())

    def _call_create_image(self, name, **kwargs):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()
        self.cloud.create_image(
            name, imagefile.name, wait=True, timeout=1,
            is_public=False, **kwargs)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_v1(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '1'
        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image('42 name')
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'properties': {
                    'owner_specified.shade.md5': mock.ANY,
                    'owner_specified.shade.sha256': mock.ANY,
                    'owner_specified.shade.object': 'images/42 name',
                    'is_public': False}}
        fake_image_dict = self._image_dict(fake_image)
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.update.assert_called_with(
            data=mock.ANY, image=meta.obj_to_dict(fake_image))
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_v2(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image('42 name', min_disk='0', min_ram=0)
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': 'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.upload.assert_called_with(
            image_data=mock.ANY, image_id=fake_image.id)
        fake_image_dict = self._image_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_bad_int(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self.assertRaises(
            exc.OpenStackCloudException,
            self._call_create_image, '42 name', min_disk='fish', min_ram=0)

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_user_int(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, int_v=12345)
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
                'int_v': '12345',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.upload.assert_called_with(
            image_data=mock.ANY, image_id=fake_image.id)
        fake_image_dict = self._image_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_meta_int(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, meta={'int_v': 12345})
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
                'int_v': 12345,
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.upload.assert_called_with(
            image_data=mock.ANY, image_id=fake_image.id)
        fake_image_dict = self._image_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_protected(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, properties={'int_v': 12345},
            protected=False)
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
                'protected': False,
                'int_v': '12345',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.upload.assert_called_with(
            image_data=mock.ANY, image_id=fake_image.id)
        fake_image_dict = self._image_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_create_image_put_user_prop(self, glance_mock, mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = False

        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = fakes.FakeImage('42', '42 name', 'success')
        glance_mock.images.create.return_value = fake_image
        glance_mock.images.list.return_value = [fake_image]
        self._call_create_image(
            '42 name', min_disk='0', min_ram=0, properties={'int_v': 12345},
            xenapi_use_agent=False)
        args = {'name': '42 name',
                'container_format': 'bare', 'disk_format': u'qcow2',
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
                'int_v': '12345',
                'xenapi_use_agent': 'False',
                'visibility': 'private',
                'min_disk': 0, 'min_ram': 0}
        glance_mock.images.create.assert_called_with(**args)
        glance_mock.images.upload.assert_called_with(
            image_data=mock.ANY, image_id=fake_image.id)
        fake_image_dict = self._image_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(occ.cloud_config.CloudConfig, 'get_api_version')
    @mock.patch.object(shade.OpenStackCloud, '_get_file_hashes')
    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    @mock.patch.object(shade.OpenStackCloud, 'swift_client')
    @mock.patch.object(shade.OpenStackCloud, 'swift_service')
    def test_create_image_task(self,
                               swift_service_mock,
                               swift_mock,
                               glance_mock,
                               get_file_hashes,
                               mock_api_version):
        mock_api_version.return_value = '2'
        self.cloud.image_api_use_tasks = True

        class Container(object):
            name = 'image_upload_v2_test_container'

        fake_container = Container()
        swift_mock.get_capabilities.return_value = {
            'swift': {
                'max_file_size': 1000
            }
        }
        swift_mock.put_container.return_value = fake_container
        swift_mock.head_object.return_value = {}
        glance_mock.images.list.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_md5 = "fake-md5"
        fake_sha256 = "fake-sha256"
        get_file_hashes.return_value = (fake_md5, fake_sha256)

        FakeImage = warlock.model_factory(shell.get_image_schema())
        fake_image = FakeImage(
            id='a35e8afc-cae9-4e38-8441-2cd465f79f7b', name='name-99',
            status='active', visibility='private')
        glance_mock.images.list.return_value = [fake_image]

        FakeTask = warlock.model_factory(_TASK_SCHEMA)
        args = {
            'id': '21FBD9A7-85EC-4E07-9D58-72F1ACF7CB1F',
            'status': 'success',
            'type': 'import',
            'result': {
                'image_id': 'a35e8afc-cae9-4e38-8441-2cd465f79f7b',
            },
        }
        fake_task = FakeTask(**args)
        glance_mock.tasks.get.return_value = fake_task
        self._call_create_image(name='name-99',
                                container='image_upload_v2_test_container')
        args = {'header': ['x-object-meta-x-shade-md5:fake-md5',
                           'x-object-meta-x-shade-sha256:fake-sha256'],
                'segment_size': 1000,
                'use_slo': True}
        swift_service_mock.upload.assert_called_with(
            container='image_upload_v2_test_container',
            objects=mock.ANY,
            options=args)

        glance_mock.tasks.create.assert_called_with(type='import', input={
            'import_from': 'image_upload_v2_test_container/name-99',
            'image_properties': {'name': 'name-99'}})
        object_path = 'image_upload_v2_test_container/name-99'
        args = {'owner_specified.shade.md5': fake_md5,
                'owner_specified.shade.sha256': fake_sha256,
                'owner_specified.shade.object': object_path,
                'image_id': 'a35e8afc-cae9-4e38-8441-2cd465f79f7b'}
        glance_mock.images.update.assert_called_with(**args)
        fake_image_dict = self._image_dict(fake_image)
        self.assertEqual([fake_image_dict], self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, 'glance_client')
    def test_cache_no_cloud_name(self, glance_mock):

        self.cloud.name = None
        fi = fakes.FakeImage(id=1, name='None Test Image', status='active')
        fi_dict = self._image_dict(fi)
        glance_mock.images.list.return_value = [fi]
        self.assertEqual(
            [fi_dict],
            self.cloud.list_images())
        # Now test that the list was cached
        fi2 = fakes.FakeImage(id=2, name='None Test Image', status='active')
        fi2_dict = self._image_dict(fi2)
        glance_mock.images.list.return_value = [fi, fi2]
        self.assertEqual(
            [fi_dict],
            self.cloud.list_images())
        # Invalidation too
        self.cloud.list_images.invalidate(self.cloud)
        self.assertEqual(
            [fi_dict, fi2_dict],
            self.cloud.list_images())


class TestBogusAuth(base.TestCase):

    def setUp(self):
        super(TestBogusAuth, self).setUp(
            cloud_config_fixture='clouds_cache.yaml')

    def test_get_auth_bogus(self):
        with testtools.ExpectedException(exc.OpenStackCloudException):
            shade.openstack_cloud(
                cloud='_bogus_test_', config=self.config)
