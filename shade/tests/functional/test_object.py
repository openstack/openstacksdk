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

"""
test_object
----------------------------------

Functional tests for `shade` object methods.
"""

import tempfile

from testtools import content

from shade.tests.functional import base


class TestObject(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestObject, self).setUp()
        if not self.demo_cloud.has_service('object-store'):
            self.skipTest('Object service not supported by cloud')

    def test_create_object(self):
        '''Test uploading small and large files.'''
        container_name = self.getUniqueString('container')
        self.addDetail('container', content.text_content(container_name))
        self.addCleanup(self.demo_cloud.delete_container, container_name)
        self.demo_cloud.create_container(container_name)
        self.assertEqual(container_name,
                         self.demo_cloud.list_containers()[0]['name'])
        sizes = (
            (64 * 1024, 1),      # 64K, one segment
            (50 * 1024 ** 2, 5)  # 50MB, 5 segments
        )
        for size, nseg in sizes:
            segment_size = round(size / nseg)
            with tempfile.NamedTemporaryFile() as sparse_file:
                sparse_file.seek(size)
                sparse_file.write("\0")
                sparse_file.flush()
                name = 'test-%d' % size
                self.demo_cloud.create_object(
                    container_name, name,
                    sparse_file.name,
                    segment_size=segment_size,
                    metadata={'foo': 'bar'})
                self.assertFalse(self.demo_cloud.is_object_stale(
                    container_name, name,
                    sparse_file.name
                    )
                )
            self.assertEqual(
                'bar', self.demo_cloud.get_object_metadata(
                    container_name, name)['x-object-meta-foo']
            )
            self.demo_cloud.update_object(container=container_name, name=name,
                                          metadata={'testk': 'testv'})
            self.assertEqual(
                'testv', self.demo_cloud.get_object_metadata(
                    container_name, name)['x-object-meta-testk']
            )
            self.assertIsNotNone(
                self.demo_cloud.get_object(container_name, name))
            self.assertEqual(
                name,
                self.demo_cloud.list_objects(container_name)[0]['name'])
            self.demo_cloud.delete_object(container_name, name)
        self.assertEqual([], self.demo_cloud.list_objects(container_name))
        self.assertEqual(container_name,
                         self.demo_cloud.list_containers()[0]['name'])
        self.demo_cloud.delete_container(container_name)
