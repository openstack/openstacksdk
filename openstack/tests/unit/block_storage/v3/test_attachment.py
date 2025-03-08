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

from openstack.block_storage.v3 import attachment
from openstack import resource
from openstack.tests.unit import base


FAKE_ID = "92dc3671-d0ab-4370-8058-c88a71661ec5"
FAKE_VOL_ID = "138e4a2e-85ef-4f96-a0d0-9f3ef9f32987"
FAKE_INSTANCE_UUID = "ee9ae89e-d4fc-4c95-93ad-d9e80f240cae"

CONNECTION_INFO = {
    "access_mode": "rw",
    "attachment_id": "92dc3671-d0ab-4370-8058-c88a71661ec5",
    "auth_enabled": True,
    "auth_username": "cinder",
    "cacheable": False,
    "cluster_name": "ceph",
    "discard": True,
    "driver_volume_type": "rbd",
    "encrypted": False,
    "hosts": ["127.0.0.1"],
    "name": "volumes/volume-138e4a2e-85ef-4f96-a0d0-9f3ef9f32987",
    "ports": ["6789"],
    "secret_type": "ceph",
    "secret_uuid": "e5d27872-64ab-4d8c-8c25-4dbdc522fbbf",
    "volume_id": "138e4a2e-85ef-4f96-a0d0-9f3ef9f32987",
}

CONNECTOR = {
    "do_local_attach": False,
    "host": "devstack-VirtualBox",
    "initiator": "iqn.2005-03.org.open-iscsi:1f6474a01f9a",
    "ip": "127.0.0.1",
    "multipath": False,
    "nqn": "nqn.2014-08.org.nvmexpress:uuid:4dfe457e-6206-4a61-b547-5a9d0e2fa557",
    "nvme_native_multipath": False,
    "os_type": "linux",
    "platform": "x86_64",
    "system_uuid": "2f4d1bf2-8a9e-864f-80ec-d265222bf145",
    "uuid": "87c73a20-e7f9-4370-ad85-5829b54675d7",
}

ATTACHMENT = {
    "id": FAKE_ID,
    "status": "attached",
    "instance": FAKE_INSTANCE_UUID,
    "volume_id": FAKE_VOL_ID,
    "attached_at": "2023-07-07T10:30:40.000000",
    "detached_at": None,
    "attach_mode": "rw",
    "connection_info": CONNECTION_INFO,
}


class TestAttachment(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.headers = {}
        self.resp.status_code = 202

        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.get = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.put = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = "3.54"

    def test_basic(self):
        sot = attachment.Attachment(ATTACHMENT)
        self.assertEqual("attachment", sot.resource_key)
        self.assertEqual("attachments", sot.resources_key)
        self.assertEqual("/attachments", sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_commit)
        self.assertIsNotNone(sot._max_microversion)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping,
        )

    def test_create_resource(self):
        sot = attachment.Attachment(**ATTACHMENT)
        self.assertEqual(ATTACHMENT["id"], sot.id)
        self.assertEqual(ATTACHMENT["status"], sot.status)
        self.assertEqual(ATTACHMENT["instance"], sot.instance)
        self.assertEqual(ATTACHMENT["volume_id"], sot.volume_id)
        self.assertEqual(ATTACHMENT["attached_at"], sot.attached_at)
        self.assertEqual(ATTACHMENT["detached_at"], sot.detached_at)
        self.assertEqual(ATTACHMENT["attach_mode"], sot.attach_mode)
        self.assertEqual(ATTACHMENT["connection_info"], sot.connection_info)

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    @mock.patch.object(resource.Resource, '_translate_response')
    def test_create_no_mode_no_instance_id(self, mock_translate, mock_mv):
        self.sess.default_microversion = "3.27"
        mock_mv.return_value = False
        sot = attachment.Attachment()
        FAKE_MODE = "rw"
        sot.create(
            self.sess,
            volume_id=FAKE_VOL_ID,
            connector=CONNECTOR,
            instance=None,
            mode=FAKE_MODE,
        )
        self.sess.post.assert_called_with(
            '/attachments',
            json={'attachment': {}},
            headers={},
            microversion="3.27",
            params={
                'volume_id': FAKE_VOL_ID,
                'connector': CONNECTOR,
                'instance': None,
                'mode': 'rw',
            },
        )
        self.sess.default_microversion = "3.54"

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    @mock.patch.object(resource.Resource, '_translate_response')
    def test_create_with_mode_with_instance_id(self, mock_translate, mock_mv):
        sot = attachment.Attachment()
        FAKE_MODE = "rw"
        sot.create(
            self.sess,
            volume_id=FAKE_VOL_ID,
            connector=CONNECTOR,
            instance=FAKE_INSTANCE_UUID,
            mode=FAKE_MODE,
        )
        self.sess.post.assert_called_with(
            '/attachments',
            json={'attachment': {}},
            headers={},
            microversion="3.54",
            params={
                'volume_id': FAKE_VOL_ID,
                'connector': CONNECTOR,
                'instance': FAKE_INSTANCE_UUID,
                'mode': FAKE_MODE,
            },
        )

    @mock.patch.object(resource.Resource, '_translate_response')
    def test_complete(self, mock_translate):
        sot = attachment.Attachment()
        sot.id = FAKE_ID
        sot.complete(self.sess)
        self.sess.post.assert_called_with(
            f'/attachments/{FAKE_ID}/action',
            json={
                'os-complete': '92dc3671-d0ab-4370-8058-c88a71661ec5',
            },
            microversion="3.54",
        )
