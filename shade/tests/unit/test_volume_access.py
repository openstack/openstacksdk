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


import mock
import testtools

import shade
from shade.tests.unit import base


class TestVolumeAccess(base.TestCase):
    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_list_volume_types(self, mock_cinder):
        volume_type = dict(
            id='voltype01', description='volume type description',
            name='name', is_public=False)
        mock_cinder.volume_types.list.return_value = [volume_type]

        self.assertTrue(self.cloud.list_volume_types())

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_get_volume_type(self, mock_cinder):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        mock_cinder.volume_types.list.return_value = [volume_type]

        volume_type_got = self.cloud.get_volume_type('name')
        self.assertEqual(volume_type_got.id, volume_type['id'])

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_get_volume_type_access(self, mock_cinder):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        volume_type_access = [
            dict(volume_type_id='voltype01', name='name', project_id='prj01'),
            dict(volume_type_id='voltype01', name='name', project_id='prj02')
        ]
        mock_cinder.volume_types.list.return_value = [volume_type]
        mock_cinder.volume_type_access.list.return_value = volume_type_access

        self.assertEqual(
            len(self.op_cloud.get_volume_type_access('name')), 2)

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_remove_volume_type_access(self, mock_cinder):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        project_001 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj01')
        project_002 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj02')
        volume_type_access = [project_001, project_002]
        mock_cinder.volume_types.list.return_value = [volume_type]
        mock_cinder.volume_type_access.list.return_value = volume_type_access

        def _fake_remove(*args, **kwargs):
            volume_type_access.pop()

        mock_cinder.volume_type_access.remove_project_access.side_effect = \
            _fake_remove

        self.assertEqual(
            len(self.op_cloud.get_volume_type_access(
                volume_type['name'])), 2)
        self.op_cloud.remove_volume_type_access(
            volume_type['name'], project_001['project_id'])

        self.assertEqual(
            len(self.op_cloud.get_volume_type_access('name')), 1)

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_add_volume_type_access(self, mock_cinder):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        project_001 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj01')
        project_002 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj02')
        volume_type_access = [project_001]
        mock_cinder.volume_types.list.return_value = [volume_type]
        mock_cinder.volume_type_access.list.return_value = volume_type_access
        mock_cinder.volume_type_access.add_project_access.return_value = None

        def _fake_add(*args, **kwargs):
            volume_type_access.append(project_002)

        mock_cinder.volume_type_access.add_project_access.side_effect = \
            _fake_add

        self.op_cloud.add_volume_type_access(
            volume_type['name'], project_002['project_id'])
        self.assertEqual(
            len(self.op_cloud.get_volume_type_access('name')), 2)

    @mock.patch.object(shade.OpenStackCloud, 'cinder_client')
    def test_add_volume_type_access_missing(self, mock_cinder):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        project_001 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj01')
        mock_cinder.volume_types.list.return_value = [volume_type]
        with testtools.ExpectedException(shade.OpenStackCloudException,
                                         "VolumeType not found: MISSING"):
            self.op_cloud.add_volume_type_access(
                "MISSING", project_001['project_id'])
