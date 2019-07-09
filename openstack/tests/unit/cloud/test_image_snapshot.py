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

from openstack.cloud import exc
from openstack.tests import fakes
from openstack.tests.unit import base


class TestImageSnapshot(base.TestCase):

    def setUp(self):
        super(TestImageSnapshot, self).setUp()
        self.server_id = str(uuid.uuid4())
        self.image_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.fake_server = fakes.make_fake_server(
            self.server_id, self.server_name)

    def test_create_image_snapshot_wait_until_active_never_active(self):
        snapshot_name = 'test-snapshot'
        fake_image = fakes.make_fake_image(self.image_id, status='pending')
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(
                method='POST',
                uri='{endpoint}/servers/{server_id}/action'.format(
                    endpoint=fakes.COMPUTE_ENDPOINT,
                    server_id=self.server_id),
                headers=dict(
                    Location='{endpoint}/images/{image_id}'.format(
                        endpoint='https://images.example.com',
                        image_id=self.image_id)),
                validate=dict(
                    json={
                        "createImage": {
                            "name": snapshot_name,
                            "metadata": {},
                        }})),
            self.get_glance_discovery_mock_dict(),
            dict(
                method='GET',
                uri='https://image.example.com/v2/images',
                json=dict(images=[fake_image])),
        ])

        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud.create_image_snapshot,
            snapshot_name, dict(id=self.server_id),
            wait=True, timeout=0.01)

        # After the fifth call, we just keep polling get images for status.
        # Due to mocking sleep, we have no clue how many times we'll call it.
        self.assert_calls(stop_after=5, do_count=False)

    def test_create_image_snapshot_wait_active(self):
        snapshot_name = 'test-snapshot'
        pending_image = fakes.make_fake_image(self.image_id, status='pending')
        fake_image = fakes.make_fake_image(self.image_id)
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(
                method='POST',
                uri='{endpoint}/servers/{server_id}/action'.format(
                    endpoint=fakes.COMPUTE_ENDPOINT,
                    server_id=self.server_id),
                headers=dict(
                    Location='{endpoint}/images/{image_id}'.format(
                        endpoint='https://images.example.com',
                        image_id=self.image_id)),
                validate=dict(
                    json={
                        "createImage": {
                            "name": snapshot_name,
                            "metadata": {},
                        }})),
            self.get_glance_discovery_mock_dict(),
            dict(
                method='GET',
                uri='https://image.example.com/v2/images',
                json=dict(images=[pending_image])),
            dict(
                method='GET',
                uri='https://image.example.com/v2/images',
                json=dict(images=[fake_image])),
        ])
        image = self.cloud.create_image_snapshot(
            'test-snapshot', dict(id=self.server_id), wait=True, timeout=2)
        self.assertEqual(image['id'], self.image_id)

        self.assert_calls()
