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

from openstack.block_storage.v3 import transfer
from openstack import resource
from openstack.tests.unit import base


FAKE_ID = "09d18b36-9e8d-4438-a4da-3f5eff5e1130"
FAKE_VOL_ID = "390de1bc-19d1-41e7-ba67-c492bb36cae5"
FAKE_VOL_NAME = "test-volume"
FAKE_TRANSFER = "7d048960-7c3f-4bf0-952f-4312fdea1dec"
FAKE_AUTH_KEY = "95bc670c0068821d"

TRANSFER = {
    "auth_key": FAKE_AUTH_KEY,
    "created_at": "2023-06-27T08:47:23.035010",
    "id": FAKE_ID,
    "name": FAKE_VOL_NAME,
    "volume_id": FAKE_VOL_ID,
}


class TestTransfer(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.headers = {}
        self.resp.status_code = 202

        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = "3.55"

    def test_basic(self):
        tr = transfer.Transfer(TRANSFER)
        self.assertEqual("transfer", tr.resource_key)
        self.assertEqual("transfers", tr.resources_key)
        self.assertEqual("/volume-transfers", tr.base_path)
        self.assertTrue(tr.allow_create)
        self.assertIsNotNone(tr._max_microversion)

        self.assertDictEqual(
            {
                "limit": "limit",
                "marker": "marker",
            },
            tr._query_mapping._mapping,
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    @mock.patch.object(resource.Resource, '_translate_response')
    def test_create(self, mock_mv, mock_translate):
        sot = transfer.Transfer()

        sot.create(self.sess, volume_id=FAKE_VOL_ID, name=FAKE_VOL_NAME)
        self.sess.post.assert_called_with(
            '/volume-transfers',
            json={'transfer': {}},
            microversion="3.55",
            headers={},
            params={'volume_id': FAKE_VOL_ID, 'name': FAKE_VOL_NAME},
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    @mock.patch.object(resource.Resource, '_translate_response')
    def test_create_pre_v355(self, mock_mv, mock_translate):
        self.sess.default_microversion = "3.0"
        sot = transfer.Transfer()

        sot.create(self.sess, volume_id=FAKE_VOL_ID, name=FAKE_VOL_NAME)
        self.sess.post.assert_called_with(
            '/os-volume-transfer',
            json={'transfer': {}},
            microversion="3.0",
            headers={},
            params={'volume_id': FAKE_VOL_ID, 'name': FAKE_VOL_NAME},
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    @mock.patch.object(resource.Resource, '_translate_response')
    def test_accept(self, mock_mv, mock_translate):
        sot = transfer.Transfer()
        sot.id = FAKE_TRANSFER

        sot.accept(self.sess, auth_key=FAKE_AUTH_KEY)
        self.sess.post.assert_called_with(
            f'volume-transfers/{FAKE_TRANSFER}/accept',
            json={
                'accept': {
                    'auth_key': FAKE_AUTH_KEY,
                }
            },
            microversion="3.55",
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    @mock.patch.object(resource.Resource, '_translate_response')
    def test_accept_pre_v355(self, mock_mv, mock_translate):
        self.sess.default_microversion = "3.0"
        sot = transfer.Transfer()
        sot.id = FAKE_TRANSFER

        sot.accept(self.sess, auth_key=FAKE_AUTH_KEY)
        self.sess.post.assert_called_with(
            f'os-volume-transfer/{FAKE_TRANSFER}/accept',
            json={
                'accept': {
                    'auth_key': FAKE_AUTH_KEY,
                }
            },
            microversion="3.0",
        )
