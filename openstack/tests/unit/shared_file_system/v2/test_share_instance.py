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

from unittest import mock

from keystoneauth1 import adapter

from openstack.shared_file_system.v2 import share_instance
from openstack.tests.unit import base

IDENTIFIER = "75559a8b-c90c-42a7-bda2-edbe86acfb7b"

EXAMPLE = {
    "status": "available",
    "progress": "100%",
    "share_id": "d94a8548-2079-4be0-b21c-0a887acd31ca",
    "availability_zone": "nova",
    "replica_state": None,
    "created_at": "2015-09-07T08:51:34.000000",
    "cast_rules_to_readonly": False,
    "share_network_id": "713df749-aac0-4a54-af52-10f6c991e80c",
    "share_server_id": "ba11930a-bf1a-4aa7-bae4-a8dfbaa3cc73",
    "host": "manila2@generic1#GENERIC1",
    "access_rules_status": "active",
    "id": IDENTIFIER,
}


class TestShareInstances(base.TestCase):
    def test_basic(self):
        share_instance_resource = share_instance.ShareInstance()
        self.assertEqual(
            'share_instances', share_instance_resource.resources_key
        )
        self.assertEqual('/share_instances', share_instance_resource.base_path)
        self.assertTrue(share_instance_resource.allow_list)
        self.assertFalse(share_instance_resource.allow_create)
        self.assertTrue(share_instance_resource.allow_fetch)
        self.assertFalse(share_instance_resource.allow_commit)
        self.assertFalse(share_instance_resource.allow_delete)

    def test_make_share_instances(self):
        share_instance_resource = share_instance.ShareInstance(**EXAMPLE)
        self.assertEqual(EXAMPLE['status'], share_instance_resource.status)
        self.assertEqual(EXAMPLE['progress'], share_instance_resource.progress)
        self.assertEqual(EXAMPLE['share_id'], share_instance_resource.share_id)
        self.assertEqual(
            EXAMPLE['availability_zone'],
            share_instance_resource.availability_zone,
        )
        self.assertEqual(
            EXAMPLE['replica_state'], share_instance_resource.replica_state
        )
        self.assertEqual(
            EXAMPLE['created_at'], share_instance_resource.created_at
        )
        self.assertEqual(
            EXAMPLE['cast_rules_to_readonly'],
            share_instance_resource.cast_rules_to_readonly,
        )
        self.assertEqual(
            EXAMPLE['share_network_id'],
            share_instance_resource.share_network_id,
        )
        self.assertEqual(
            EXAMPLE['share_server_id'], share_instance_resource.share_server_id
        )
        self.assertEqual(EXAMPLE['host'], share_instance_resource.host)
        self.assertEqual(
            EXAMPLE['access_rules_status'],
            share_instance_resource.access_rules_status,
        )
        self.assertEqual(EXAMPLE['id'], share_instance_resource.id)


class TestShareInstanceActions(TestShareInstances):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = '3.0'
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_reset_status(self):
        sot = share_instance.ShareInstance(**EXAMPLE)
        microversion = sot._get_microversion(self.sess)

        self.assertIsNone(sot.reset_status(self.sess, 'active'))

        url = f'share_instances/{IDENTIFIER}/action'
        body = {"reset_status": {"status": 'active'}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion=microversion
        )

    def test_force_delete(self):
        sot = share_instance.ShareInstance(**EXAMPLE)
        microversion = sot._get_microversion(self.sess)

        self.assertIsNone(sot.force_delete(self.sess))

        url = f'share_instances/{IDENTIFIER}/action'
        body = {'force_delete': None}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(
            url, json=body, headers=headers, microversion=microversion
        )
