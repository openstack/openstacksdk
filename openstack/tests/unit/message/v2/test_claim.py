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

import copy
from unittest import mock
import uuid

from openstack.message.v2 import claim
from openstack.tests.unit import base

FAKE1 = {
    "age": 1632,
    "id": "576b54963990b48c644bb7e7",
    "grace": 3600,
    "limit": 10,
    "messages": [{"id": "1"}, {"id": "2"}],
    "ttl": 3600,
    "queue_name": "queue1",
}


FAKE2 = {
    "age": 1632,
    "id": "576b54963990b48c644bb7e7",
    "grace": 3600,
    "limit": 10,
    "messages": [{"id": "1"}, {"id": "2"}],
    "ttl": 3600,
    "queue_name": "queue1",
    "client_id": "OLD_CLIENT_ID",
    "project_id": "OLD_PROJECT_ID",
}


class TestClaim(base.TestCase):
    def test_basic(self):
        sot = claim.Claim()
        self.assertEqual("claims", sot.resources_key)
        self.assertEqual("/queues/%(queue_name)s/claims", sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_commit)

    def test_make_it(self):
        sot = claim.Claim.new(**FAKE2)
        self.assertEqual(FAKE2["age"], sot.age)
        self.assertEqual(FAKE2["id"], sot.id)
        self.assertEqual(FAKE2["grace"], sot.grace)
        self.assertEqual(FAKE2["limit"], sot.limit)
        self.assertEqual(FAKE2["messages"], sot.messages)
        self.assertEqual(FAKE2["ttl"], sot.ttl)
        self.assertEqual(FAKE2["queue_name"], sot.queue_name)
        self.assertEqual(FAKE2["client_id"], sot.client_id)
        self.assertEqual(FAKE2["project_id"], sot.project_id)

    @mock.patch.object(uuid, "uuid4")
    def test_create_204_resp(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.post.return_value = resp
        resp.status_code = 204
        sess.get_project_id.return_value = "NEW_PROJECT_ID"
        mock_uuid.return_value = "NEW_CLIENT_ID"
        FAKE = copy.deepcopy(FAKE1)

        sot = claim.Claim(**FAKE1)
        res = sot.create(sess)

        url = "/queues/{queue}/claims".format(queue=FAKE.pop("queue_name"))
        headers = {
            "Client-ID": "NEW_CLIENT_ID",
            "X-PROJECT-ID": "NEW_PROJECT_ID",
        }
        sess.post.assert_called_once_with(url, headers=headers, json=FAKE)
        sess.get_project_id.assert_called_once_with()
        self.assertEqual(sot, res)

    @mock.patch.object(uuid, "uuid4")
    def test_create_non_204_resp(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.post.return_value = resp
        resp.status_code = 200
        sess.get_project_id.return_value = "NEW_PROJECT_ID"
        mock_uuid.return_value = "NEW_CLIENT_ID"
        FAKE = copy.deepcopy(FAKE1)

        sot = claim.Claim(**FAKE1)
        sot._translate_response = mock.Mock()
        res = sot.create(sess)

        url = "/queues/{queue}/claims".format(queue=FAKE.pop("queue_name"))
        headers = {
            "Client-ID": "NEW_CLIENT_ID",
            "X-PROJECT-ID": "NEW_PROJECT_ID",
        }
        sess.post.assert_called_once_with(url, headers=headers, json=FAKE)
        sess.get_project_id.assert_called_once_with()
        self.assertEqual(sot, res)
        sot._translate_response.assert_called_once_with(resp)

    def test_create_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.post.return_value = resp
        resp.status_code = 200
        FAKE = copy.deepcopy(FAKE2)

        sot = claim.Claim(**FAKE2)
        sot._translate_response = mock.Mock()
        res = sot.create(sess)

        url = "/queues/{queue}/claims".format(queue=FAKE.pop("queue_name"))
        headers = {
            "Client-ID": FAKE.pop("client_id"),
            "X-PROJECT-ID": FAKE.pop("project_id"),
        }
        sess.post.assert_called_once_with(url, headers=headers, json=FAKE)
        self.assertEqual(sot, res)

    @mock.patch.object(uuid, "uuid4")
    def test_get(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp
        sess.get_project_id.return_value = "NEW_PROJECT_ID"
        mock_uuid.return_value = "NEW_CLIENT_ID"

        sot = claim.Claim(**FAKE1)
        sot._translate_response = mock.Mock()
        res = sot.fetch(sess)

        url = "queues/{queue}/claims/{claim}".format(
            queue=FAKE1["queue_name"],
            claim=FAKE1["id"],
        )
        headers = {
            "Client-ID": "NEW_CLIENT_ID",
            "X-PROJECT-ID": "NEW_PROJECT_ID",
        }
        sess.get.assert_called_with(url, headers=headers, skip_cache=False)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp)
        self.assertEqual(sot, res)

    def test_get_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp

        sot = claim.Claim(**FAKE2)
        sot._translate_response = mock.Mock()
        res = sot.fetch(sess)

        url = "queues/{queue}/claims/{claim}".format(
            queue=FAKE2["queue_name"],
            claim=FAKE2["id"],
        )
        headers = {
            "Client-ID": "OLD_CLIENT_ID",
            "X-PROJECT-ID": "OLD_PROJECT_ID",
        }
        sess.get.assert_called_with(url, headers=headers, skip_cache=False)
        sot._translate_response.assert_called_once_with(resp)
        self.assertEqual(sot, res)

    @mock.patch.object(uuid, "uuid4")
    def test_update(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.update.return_value = resp
        sess.get_project_id.return_value = "NEW_PROJECT_ID"
        mock_uuid.return_value = "NEW_CLIENT_ID"
        FAKE = copy.deepcopy(FAKE1)

        sot = claim.Claim(**FAKE1)
        res = sot.commit(sess)

        url = "queues/{queue}/claims/{claim}".format(
            queue=FAKE.pop("queue_name"),
            claim=FAKE["id"],
        )
        headers = {
            "Client-ID": "NEW_CLIENT_ID",
            "X-PROJECT-ID": "NEW_PROJECT_ID",
        }
        sess.patch.assert_called_with(url, headers=headers, json=FAKE)
        sess.get_project_id.assert_called_once_with()
        self.assertEqual(sot, res)

    def test_update_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.get.return_value = resp
        FAKE = copy.deepcopy(FAKE2)

        sot = claim.Claim(**FAKE2)
        res = sot.commit(sess)

        url = "queues/{queue}/claims/{claim}".format(
            queue=FAKE.pop("queue_name"),
            claim=FAKE["id"],
        )
        headers = {
            "Client-ID": FAKE.pop("client_id"),
            "X-PROJECT-ID": FAKE.pop("project_id"),
        }
        sess.patch.assert_called_with(url, headers=headers, json=FAKE)
        self.assertEqual(sot, res)

    @mock.patch.object(uuid, "uuid4")
    def test_delete(self, mock_uuid):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp
        sess.get_project_id.return_value = "NEW_PROJECT_ID"
        mock_uuid.return_value = "NEW_CLIENT_ID"

        sot = claim.Claim(**FAKE1)
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = "queues/{queue}/claims/{claim}".format(
            queue=FAKE1["queue_name"],
            claim=FAKE1["id"],
        )
        headers = {
            "Client-ID": "NEW_CLIENT_ID",
            "X-PROJECT-ID": "NEW_PROJECT_ID",
        }
        sess.delete.assert_called_with(url, headers=headers)
        sess.get_project_id.assert_called_once_with()
        sot._translate_response.assert_called_once_with(resp, has_body=False)

    def test_delete_client_id_project_id_exist(self):
        sess = mock.Mock()
        resp = mock.Mock()
        sess.delete.return_value = resp

        sot = claim.Claim(**FAKE2)
        sot._translate_response = mock.Mock()
        sot.delete(sess)

        url = "queues/{queue}/claims/{claim}".format(
            queue=FAKE2["queue_name"],
            claim=FAKE2["id"],
        )
        headers = {
            "Client-ID": "OLD_CLIENT_ID",
            "X-PROJECT-ID": "OLD_PROJECT_ID",
        }
        sess.delete.assert_called_with(url, headers=headers)
        sot._translate_response.assert_called_once_with(resp, has_body=False)
