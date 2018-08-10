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
test_object
----------------------------------

Functional tests for `shade` object methods.
"""

import random
import string
import tempfile

from testtools import content

from openstack.cloud import exc
from openstack.tests.functional import base


class TestObject(base.BaseFunctionalTest):

    def setUp(self):
        super(TestObject, self).setUp()
        if not self.user_cloud.has_service('object-store'):
            self.skipTest('Object service not supported by cloud')

    def test_create_object(self):
        '''Test uploading small and large files.'''
        container_name = self.getUniqueString('container')
        self.addDetail('container', content.text_content(container_name))
        self.addCleanup(self.user_cloud.delete_container, container_name)
        self.user_cloud.create_container(container_name)
        self.assertEqual(container_name,
                         self.user_cloud.list_containers()[0]['name'])
        sizes = (
            (64 * 1024, 1),  # 64K, one segment
            (64 * 1024, 5)   # 64MB, 5 segments
        )
        for size, nseg in sizes:
            segment_size = int(round(size / nseg))
            with tempfile.NamedTemporaryFile() as fake_file:
                fake_content = ''.join(random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits)
                    for _ in range(size)).encode('latin-1')

                fake_file.write(fake_content)
                fake_file.flush()
                name = 'test-%d' % size
                self.addCleanup(
                    self.user_cloud.delete_object, container_name, name)
                self.user_cloud.create_object(
                    container_name, name,
                    fake_file.name,
                    segment_size=segment_size,
                    metadata={'foo': 'bar'})
                self.assertFalse(self.user_cloud.is_object_stale(
                    container_name, name,
                    fake_file.name
                ))
            self.assertEqual(
                'bar', self.user_cloud.get_object_metadata(
                    container_name, name)['x-object-meta-foo']
            )
            self.user_cloud.update_object(container=container_name, name=name,
                                          metadata={'testk': 'testv'})
            self.assertEqual(
                'testv', self.user_cloud.get_object_metadata(
                    container_name, name)['x-object-meta-testk']
            )
            try:
                self.assertIsNotNone(
                    self.user_cloud.get_object(container_name, name))
            except exc.OpenStackCloudException as e:
                self.addDetail(
                    'failed_response',
                    content.text_content(str(e.response.headers)))
                self.addDetail(
                    'failed_response',
                    content.text_content(e.response.text))
            self.assertEqual(
                name,
                self.user_cloud.list_objects(container_name)[0]['name'])
            self.assertTrue(
                self.user_cloud.delete_object(container_name, name))
        self.assertEqual([], self.user_cloud.list_objects(container_name))
        self.assertEqual(container_name,
                         self.user_cloud.list_containers()[0]['name'])
        self.user_cloud.delete_container(container_name)

    def test_download_object_to_file(self):
        '''Test uploading small and large files.'''
        container_name = self.getUniqueString('container')
        self.addDetail('container', content.text_content(container_name))
        self.addCleanup(self.user_cloud.delete_container, container_name)
        self.user_cloud.create_container(container_name)
        self.assertEqual(container_name,
                         self.user_cloud.list_containers()[0]['name'])
        sizes = (
            (64 * 1024, 1),  # 64K, one segment
            (64 * 1024, 5)   # 64MB, 5 segments
        )
        for size, nseg in sizes:
            fake_content = ''
            segment_size = int(round(size / nseg))
            with tempfile.NamedTemporaryFile() as fake_file:
                fake_content = ''.join(random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits)
                    for _ in range(size)).encode('latin-1')

                fake_file.write(fake_content)
                fake_file.flush()
                name = 'test-%d' % size
                self.addCleanup(
                    self.user_cloud.delete_object, container_name, name)
                self.user_cloud.create_object(
                    container_name, name,
                    fake_file.name,
                    segment_size=segment_size,
                    metadata={'foo': 'bar'})
                self.assertFalse(self.user_cloud.is_object_stale(
                    container_name, name,
                    fake_file.name
                ))
            self.assertEqual(
                'bar', self.user_cloud.get_object_metadata(
                    container_name, name)['x-object-meta-foo']
            )
            self.user_cloud.update_object(container=container_name, name=name,
                                          metadata={'testk': 'testv'})
            self.assertEqual(
                'testv', self.user_cloud.get_object_metadata(
                    container_name, name)['x-object-meta-testk']
            )
            try:
                with tempfile.NamedTemporaryFile() as fake_file:
                    self.user_cloud.get_object(
                        container_name, name, outfile=fake_file.name)
                    downloaded_content = open(fake_file.name, 'rb').read()
                    self.assertEqual(fake_content, downloaded_content)
            except exc.OpenStackCloudException as e:
                self.addDetail(
                    'failed_response',
                    content.text_content(str(e.response.headers)))
                self.addDetail(
                    'failed_response',
                    content.text_content(e.response.text))
                raise
            self.assertEqual(
                name,
                self.user_cloud.list_objects(container_name)[0]['name'])
            self.assertTrue(
                self.user_cloud.delete_object(container_name, name))
        self.assertEqual([], self.user_cloud.list_objects(container_name))
        self.assertEqual(container_name,
                         self.user_cloud.list_containers()[0]['name'])
        self.user_cloud.delete_container(container_name)
