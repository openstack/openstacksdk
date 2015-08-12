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
import uuid

from testtools import content

from shade import openstack_cloud
from shade.tests import base


class TestObject(base.TestCase):

    def setUp(self):
        super(TestObject, self).setUp()
        self.cloud = openstack_cloud(cloud='devstack')
        if not self.cloud.has_service('object'):
            self.skipTest('Object service not supported by cloud')

    def test_create_object(self):
        '''Test uploading small and large files.'''
        container = str(uuid.uuid4())
        self.addDetail('container', content.text_content(container))
        self.addCleanup(self.cloud.delete_container, container)
        self.cloud.create_container(container)
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
                self.cloud.create_object(container, name, sparse_file.name,
                                         segment_size=segment_size)
                self.assertFalse(self.cloud.is_object_stale(container, name,
                                                            sparse_file.name))
            self.assertIsNotNone(
                self.cloud.get_object_metadata(container, name))
            self.cloud.delete_object(container, name)
        self.cloud.delete_container(container)
