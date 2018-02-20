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


import testtools

import openstack.cloud
from openstack.tests.unit import base


class TestVolumeAccess(base.TestCase):
    def test_list_volume_types(self):
        volume_type = dict(
            id='voltype01', description='volume type description',
            name='name', is_public=False)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]})])
        self.assertTrue(self.cloud.list_volume_types())
        self.assert_calls()

    def test_get_volume_type(self):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]})])
        volume_type_got = self.cloud.get_volume_type(volume_type['name'])
        self.assertEqual(volume_type_got.id, volume_type['id'])

    def test_get_volume_type_access(self):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        volume_type_access = [
            dict(volume_type_id='voltype01', name='name', project_id='prj01'),
            dict(volume_type_id='voltype01', name='name', project_id='prj02')
        ]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types', volume_type['id'],
                             'os-volume-type-access']),
                 json={'volume_type_access': volume_type_access})])
        self.assertEqual(
            len(self.cloud.get_volume_type_access(volume_type['name'])), 2)
        self.assert_calls()

    def test_remove_volume_type_access(self):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        project_001 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj01')
        project_002 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj02')
        volume_type_access = [project_001, project_002]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types', volume_type['id'],
                             'os-volume-type-access']),
                 json={'volume_type_access': volume_type_access}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'], qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types', volume_type['id'], 'action']),
                 json={'removeProjectAccess': {
                       'project': project_001['project_id']}},
                 validate=dict(
                     json={'removeProjectAccess': {
                         'project': project_001['project_id']}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types', volume_type['id'],
                             'os-volume-type-access']),
                 json={'volume_type_access': [project_001]})])
        self.assertEqual(
            len(self.cloud.get_volume_type_access(
                volume_type['name'])), 2)
        self.cloud.remove_volume_type_access(
            volume_type['name'], project_001['project_id'])
        self.assertEqual(
            len(self.cloud.get_volume_type_access(volume_type['name'])), 1)
        self.assert_calls()

    def test_add_volume_type_access(self):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        project_001 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj01')
        project_002 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj02')
        volume_type_access = [project_001, project_002]
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types', volume_type['id'], 'action']),
                 json={'addProjectAccess': {
                       'project': project_002['project_id']}},
                 validate=dict(
                     json={'addProjectAccess': {
                         'project': project_002['project_id']}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types', volume_type['id'],
                             'os-volume-type-access']),
                 json={'volume_type_access': volume_type_access})])
        self.cloud.add_volume_type_access(
            volume_type['name'], project_002['project_id'])
        self.assertEqual(
            len(self.cloud.get_volume_type_access(volume_type['name'])), 2)
        self.assert_calls()

    def test_add_volume_type_access_missing(self):
        volume_type = dict(
            id='voltype01', description='volume type description', name='name',
            is_public=False)
        project_001 = dict(volume_type_id='voltype01', name='name',
                           project_id='prj01')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'volumev2', 'public',
                     append=['types'],
                     qs_elements=['is_public=None']),
                 json={'volume_types': [volume_type]})])
        with testtools.ExpectedException(
                openstack.cloud.OpenStackCloudException,
                "VolumeType not found: MISSING"):
            self.cloud.add_volume_type_access(
                "MISSING", project_001['project_id'])
        self.assert_calls()
