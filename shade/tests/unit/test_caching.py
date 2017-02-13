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
import time

import mock
import munch
import testtools

import shade.openstackcloud
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


class TestMemoryCache(base.RequestsMockTestCase):

    def setUp(self):
        super(TestMemoryCache, self).setUp(
            cloud_config_fixture='clouds_cache.yaml')

    def _image_dict(self, fake_image):
        return self.cloud._normalize_image(meta.obj_to_dict(fake_image))

    def _munch_images(self, fake_image):
        return self.cloud._normalize_images([fake_image])

    def test_openstack_cloud(self):
        self.assertIsInstance(self.cloud, shade.OpenStackCloud)

    def test_list_projects_v3(self):
        self._add_discovery_uri_call()
        project_one = self._get_project_data()
        project_two = self._get_project_data()
        project_list = [project_one, project_two]

        first_response = {'projects': [project_one.json_response['project']]}
        second_response = {'projects': [p.json_response['project']
                                        for p in project_list]}

        mock_uri = self.get_mock_url(
            service_type='identity', interface='admin', resource='projects',
            base_url_append='v3')

        self.register_uris([
            dict(method='GET', uri=mock_uri, status_code=200,
                 json=first_response),
            dict(method='GET', uri=mock_uri, status_code=200,
                 json=second_response)])

        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict(first_response['projects'])),
            self.cloud.list_projects())
        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict(first_response['projects'])),
            self.cloud.list_projects())
        # invalidate the list_projects cache
        self.cloud.list_projects.invalidate(self.cloud)
        # ensure the new values are now retrieved
        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict(second_response['projects'])),
            self.cloud.list_projects())
        self.assert_calls()

    def test_list_projects_v2(self):
        self.use_keystone_v2()
        project_one = self._get_project_data(v3=False)
        project_two = self._get_project_data(v3=False)
        project_list = [project_one, project_two]

        first_response = {'tenants': [project_one.json_response['tenant']]}
        second_response = {'tenants': [p.json_response['tenant']
                                       for p in project_list]}

        mock_uri = self.get_mock_url(
            service_type='identity', interface='admin', resource='tenants')

        self.register_uris([
            dict(method='GET', uri=mock_uri, status_code=200,
                 json=first_response),
            dict(method='GET', uri=mock_uri, status_code=200,
                 json=second_response)])

        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict(first_response['tenants'])),
            self.cloud.list_projects())
        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict(first_response['tenants'])),
            self.cloud.list_projects())
        # invalidate the list_projects cache
        self.cloud.list_projects.invalidate(self.cloud)
        # ensure the new values are now retrieved
        self.assertEqual(
            self.cloud._normalize_projects(
                meta.obj_list_to_dict(second_response['tenants'])),
            self.cloud.list_projects())
        self.assert_calls()

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
        fake_volume_dict = self.cloud._normalize_volume(
            meta.obj_to_dict(fake_volume))
        cinder_mock.volumes.list.return_value = [fake_volume]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        fake_volume2 = fakes.FakeVolume('volume2', 'available',
                                        'Volume 2 Display Name')
        fake_volume2_dict = self.cloud._normalize_volume(
            meta.obj_to_dict(fake_volume2))
        cinder_mock.volumes.list.return_value = [fake_volume, fake_volume2]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        self.cloud.list_volumes.invalidate(self.cloud)
        self.assertEqual([fake_volume_dict, fake_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch('shade.OpenStackCloud.cinder_client')
    def test_list_volumes_creating_invalidates(self, cinder_mock):
        fake_volume = fakes.FakeVolume('volume1', 'creating',
                                       'Volume 1 Display Name')
        fake_volume_dict = self.cloud._normalize_volume(
            meta.obj_to_dict(fake_volume))
        cinder_mock.volumes.list.return_value = [fake_volume]
        self.assertEqual([fake_volume_dict], self.cloud.list_volumes())
        fake_volume2 = fakes.FakeVolume('volume2', 'available',
                                        'Volume 2 Display Name')
        fake_volume2_dict = self.cloud._normalize_volume(
            meta.obj_to_dict(fake_volume2))
        cinder_mock.volumes.list.return_value = [fake_volume, fake_volume2]
        self.assertEqual([fake_volume_dict, fake_volume2_dict],
                         self.cloud.list_volumes())

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_create_volume_invalidates(self, cinder_mock):
        fake_volb4 = fakes.FakeVolume('volume1', 'available',
                                      'Volume 1 Display Name')
        fake_volb4_dict = self.cloud._normalize_volume(
            meta.obj_to_dict(fake_volb4))
        cinder_mock.volumes.list.return_value = [fake_volb4]
        self.assertEqual([fake_volb4_dict], self.cloud.list_volumes())
        volume = dict(display_name='junk_vol',
                      size=1,
                      display_description='test junk volume')
        fake_vol = fakes.FakeVolume('12345', 'creating', '')
        fake_vol_dict = meta.obj_to_dict(fake_vol)
        fake_vol_dict = self.cloud._normalize_volume(
            meta.obj_to_dict(fake_vol))
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

    def test_list_users(self):
        self._add_discovery_uri_call()
        user_data = self._get_user_data(email='test@example.com')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     service_type='identity',
                     interface='admin',
                     resource='users',
                     base_url_append='v3'),
                 status_code=200,
                 json={'users': [user_data.json_response['user']]})])
        users = self.cloud.list_users()
        self.assertEqual(1, len(users))
        self.assertEqual(user_data.user_id, users[0]['id'])
        self.assertEqual(user_data.name, users[0]['name'])
        self.assertEqual(user_data.email, users[0]['email'])
        self.assert_calls()

    def test_modify_user_invalidates_cache(self):
        self.use_keystone_v2()

        user_data = self._get_user_data(email='test@example.com')
        new_resp = {'user': user_data.json_response['user'].copy()}
        new_resp['user']['email'] = 'Nope@Nope.Nope'
        new_req = {'user': {'email': new_resp['user']['email']}}

        mock_users_url = self.get_mock_url(
            service_type='identity',
            interface='admin',
            resource='users')
        mock_user_resource_url = self.get_mock_url(
            service_type='identity',
            interface='admin',
            resource='users',
            append=[user_data.user_id])

        empty_user_list_resp = {'users': []}
        users_list_resp = {'users': [user_data.json_response['user']]}
        updated_users_list_resp = {'users': [new_resp['user']]}

        uris_to_mock = [
            # Inital User List is Empty
            dict(method='GET', uri=mock_users_url, status_code=200,
                 json=empty_user_list_resp),
            # POST to create the user
            # GET to get the user data after POST
            dict(method='POST', uri=mock_users_url, status_code=200,
                 json=user_data.json_response,
                 validate=user_data.json_request),
            dict(method='GET', uri=mock_user_resource_url, status_code=200,
                 json=user_data.json_response),
            # List Users Call
            dict(method='GET', uri=mock_users_url, status_code=200,
                 json=users_list_resp),
            # List users to get ID for update
            # Get user using user_id from list
            # Update user
            # Get updated user
            dict(method='GET', uri=mock_users_url, status_code=200,
                 json=users_list_resp),
            dict(method='GET', uri=mock_user_resource_url, status_code=200,
                 json=user_data.json_response),
            dict(method='PUT', uri=mock_user_resource_url, status_code=200,
                 json=new_resp, validate=new_req),
            dict(method='GET', uri=mock_user_resource_url, status_code=200,
                 json=new_resp),
            # List Users Call
            dict(method='GET', uri=mock_users_url, status_code=200,
                 json=updated_users_list_resp),
            # List User to get ID for delete
            # Get user using user_id from list
            # delete user
            dict(method='GET', uri=mock_users_url, status_code=200,
                 json=updated_users_list_resp),
            dict(method='GET', uri=mock_user_resource_url, status_code=200,
                 json=new_resp),
            dict(method='DELETE', uri=mock_user_resource_url, status_code=204),
            # List Users Call (empty post delete)
            dict(method='GET', uri=mock_users_url, status_code=200,
                 json=empty_user_list_resp)
        ]

        self.register_uris(uris_to_mock)

        # first cache an empty list
        self.assertEqual([], self.cloud.list_users())

        # now add one
        created = self.cloud.create_user(name=user_data.name,
                                         email=user_data.email)
        self.assertEqual(user_data.user_id, created['id'])
        self.assertEqual(user_data.name, created['name'])
        self.assertEqual(user_data.email, created['email'])
        # Cache should have been invalidated
        users = self.cloud.list_users()
        self.assertEqual(user_data.user_id, users[0]['id'])
        self.assertEqual(user_data.name, users[0]['name'])
        self.assertEqual(user_data.email, users[0]['email'])

        # Update and check to see if it is updated
        updated = self.cloud.update_user(user_data.user_id,
                                         email=new_resp['user']['email'])
        self.assertEqual(user_data.user_id, updated.id)
        self.assertEqual(user_data.name, updated.name)
        self.assertEqual(new_resp['user']['email'], updated.email)
        users = self.cloud.list_users()
        self.assertEqual(1, len(users))
        self.assertEqual(user_data.user_id, users[0]['id'])
        self.assertEqual(user_data.name, users[0]['name'])
        self.assertEqual(new_resp['user']['email'], users[0]['email'])
        # Now delete and ensure it disappears
        self.cloud.delete_user(user_data.user_id)
        self.assertEqual([], self.cloud.list_users())
        self.assert_calls()

    def test_list_flavors(self):
        mock_uri = '{endpoint}/flavors/detail?is_public=None'.format(
            endpoint=fakes.COMPUTE_ENDPOINT)

        uris_to_mock = [
            dict(method='GET', uri=mock_uri, json={'flavors': []}),
            dict(method='GET', uri=mock_uri,
                 json={'flavors': fakes.FAKE_FLAVOR_LIST})
        ]
        uris_to_mock.extend([
            dict(method='GET',
                 uri='{endpoint}/flavors/{id}/os-extra_specs'.format(
                     endpoint=fakes.COMPUTE_ENDPOINT, id=flavor['id']),
                 json={'extra_specs': {}})
            for flavor in fakes.FAKE_FLAVOR_LIST])

        self.register_uris(uris_to_mock)

        self.assertEqual([], self.cloud.list_flavors())

        self.assertEqual([], self.cloud.list_flavors())

        fake_flavor_dicts = self.cloud._normalize_flavors(
            fakes.FAKE_FLAVOR_LIST)
        self.cloud.list_flavors.invalidate(self.cloud)
        self.assertEqual(fake_flavor_dicts, self.cloud.list_flavors())

        self.assert_calls()

    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_list_images(self, mock_image_client):
        mock_image_client.get.return_value = []
        self.assertEqual([], self.cloud.list_images())

        fake_image = munch.Munch(
            id='42', status='success', name='42 name',
            container_format='bare',
            disk_format='qcow2',
            properties={
                'owner_specified.shade.md5': mock.ANY,
                'owner_specified.shade.sha256': mock.ANY,
                'owner_specified.shade.object': 'images/42 name',
                'is_public': False})
        mock_image_client.get.return_value = [fake_image]
        self.assertEqual([], self.cloud.list_images())
        self.cloud.list_images.invalidate(self.cloud)
        self.assertEqual(
            self._munch_images(fake_image), self.cloud.list_images())
        mock_image_client.get.assert_called_with('/images')

    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_list_images_ignores_unsteady_status(self, mock_image_client):
        steady_image = munch.Munch(id='68', name='Jagr', status='active')
        for status in ('queued', 'saving', 'pending_delete'):
            active_image = munch.Munch(
                id=self.getUniqueString(), name=self.getUniqueString(),
                status=status)
            mock_image_client.get.return_value = [active_image]

            self.assertEqual(
                self._munch_images(active_image),
                self.cloud.list_images())
            mock_image_client.get.return_value = [
                active_image, steady_image]
            # Should expect steady_image to appear if active wasn't cached
            self.assertEqual(
                [self._image_dict(active_image),
                 self._image_dict(steady_image)],
                self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_list_images_caches_steady_status(self, mock_image_client):
        steady_image = munch.Munch(id='91', name='Federov', status='active')
        first_image = None
        for status in ('active', 'deleted', 'killed'):
            active_image = munch.Munch(
                id=self.getUniqueString(), name=self.getUniqueString(),
                status=status)
            mock_image_client.get.return_value = [active_image]
            if not first_image:
                first_image = active_image
            self.assertEqual(
                self._munch_images(first_image),
                self.cloud.list_images())
            mock_image_client.get.return_value = [
                active_image, steady_image]
            # because we skipped the create_image code path, no invalidation
            # was done, so we _SHOULD_ expect steady state images to cache and
            # therefore we should _not_ expect to see the new one here
            self.assertEqual(
                self._munch_images(first_image),
                self.cloud.list_images())

    @mock.patch.object(shade.OpenStackCloud, '_image_client')
    def test_cache_no_cloud_name(self, mock_image_client):

        self.cloud.name = None
        fi = munch.Munch(
            id='1', name='None Test Image',
            status='active', visibility='private')
        mock_image_client.get.return_value = [fi]
        self.assertEqual(
            self._munch_images(fi),
            self.cloud.list_images())
        # Now test that the list was cached
        fi2 = munch.Munch(
            id='2', name='None Test Image',
            status='active', visibility='private')
        mock_image_client.get.return_value = [fi, fi2]
        self.assertEqual(
            self._munch_images(fi),
            self.cloud.list_images())
        # Invalidation too
        self.cloud.list_images.invalidate(self.cloud)
        self.assertEqual(
            [self._image_dict(fi), self._image_dict(fi2)],
            self.cloud.list_images())


class TestBogusAuth(base.TestCase):

    def setUp(self):
        super(TestBogusAuth, self).setUp(
            cloud_config_fixture='clouds_cache.yaml')

    def test_get_auth_bogus(self):
        with testtools.ExpectedException(exc.OpenStackCloudException):
            shade.openstack_cloud(
                cloud='_bogus_test_', config=self.config)
