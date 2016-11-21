# Copyright 2016 Hewlett-Packard Development Company, L.P.
#
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

import uuid

import mock

import shade
from shade import exc
from shade.tests.unit import base


class TestImageSnapshot(base.TestCase):

    def setUp(self):
        super(TestImageSnapshot, self).setUp()
        self.image_id = str(uuid.uuid4())

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    @mock.patch.object(shade.OpenStackCloud, 'get_image')
    def test_create_image_snapshot_wait_until_active_never_active(self,
                                                                  mock_get,
                                                                  mock_nova):
        mock_nova.servers.create_image.return_value = {
            'status': 'queued',
            'id': self.image_id,
        }
        mock_get.return_value = {'status': 'saving', 'id': self.image_id}
        self.assertRaises(exc.OpenStackCloudTimeout,
                          self.cloud.create_image_snapshot,
                          'test-snapshot', dict(id='fake-server'),
                          wait=True, timeout=0.01)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    @mock.patch.object(shade.OpenStackCloud, 'get_image')
    def test_create_image_snapshot_wait_active(self, mock_get, mock_nova):
        mock_nova.servers.create_image.return_value = {
            'status': 'queued',
            'id': self.image_id,
        }
        mock_get.return_value = {'status': 'active', 'id': self.image_id}
        image = self.cloud.create_image_snapshot(
            'test-snapshot', dict(id='fake-server'), wait=True, timeout=2)
        self.assertEqual(image['id'], self.image_id)

    @mock.patch.object(shade.OpenStackCloud, 'get_server')
    def test_create_image_snapshot_bad_name_exception(
            self, mock_get_server):
        mock_get_server.return_value = None
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_image_snapshot,
            'test-snapshot', 'missing-server')
