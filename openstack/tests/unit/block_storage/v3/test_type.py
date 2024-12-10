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

from openstack.block_storage.v3 import type
from openstack import exceptions
from openstack.tests.unit import base


FAKE_ID = "6685584b-1eac-4da6-b5c3-555430cf68ff"
TYPE = {
    "extra_specs": {"capabilities": "gpu"},
    "id": FAKE_ID,
    "name": "SSD",
    "description": "Test type",
}


class TestType(base.TestCase):
    def setUp(self):
        super().setUp()
        self.extra_specs_result = {"extra_specs": {"go": "cubs", "boo": "sox"}}
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = '3.0'
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_basic(self):
        sot = type.Type(**TYPE)
        self.assertEqual("volume_type", sot.resource_key)
        self.assertEqual("volume_types", sot.resources_key)
        self.assertEqual("/types", sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_commit)

    def test_new(self):
        sot = type.Type.new(id=FAKE_ID)
        self.assertEqual(FAKE_ID, sot.id)

    def test_create(self):
        sot = type.Type(**TYPE)
        self.assertEqual(TYPE["id"], sot.id)
        self.assertEqual(TYPE["extra_specs"], sot.extra_specs)
        self.assertEqual(TYPE["name"], sot.name)
        self.assertEqual(TYPE["description"], sot.description)

    def test_set_extra_specs(self):
        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = self.extra_specs_result
        sess = mock.Mock()
        sess.post.return_value = response

        sot = type.Type(id=FAKE_ID)

        set_specs = {"lol": "rofl"}

        result = sot.set_extra_specs(sess, **set_specs)

        self.assertEqual(result, self.extra_specs_result["extra_specs"])
        sess.post.assert_called_once_with(
            "types/" + FAKE_ID + "/extra_specs",
            headers={},
            json={"extra_specs": set_specs},
        )

    def test_set_extra_specs_error(self):
        sess = mock.Mock()
        response = mock.Mock()
        response.status_code = 400
        response.content = None
        sess.post.return_value = response

        sot = type.Type(id=FAKE_ID)

        set_specs = {"lol": "rofl"}

        self.assertRaises(
            exceptions.BadRequestException,
            sot.set_extra_specs,
            sess,
            **set_specs,
        )

    def test_delete_extra_specs(self):
        sess = mock.Mock()
        response = mock.Mock()
        response.status_code = 200
        sess.delete.return_value = response

        sot = type.Type(id=FAKE_ID)

        key = "hey"

        sot.delete_extra_specs(sess, [key])

        sess.delete.assert_called_once_with(
            "types/" + FAKE_ID + "/extra_specs/" + key,
            headers={},
        )

    def test_delete_extra_specs_error(self):
        sess = mock.Mock()
        response = mock.Mock()
        response.status_code = 400
        response.content = None
        sess.delete.return_value = response

        sot = type.Type(id=FAKE_ID)

        key = "hey"

        self.assertRaises(
            exceptions.BadRequestException, sot.delete_extra_specs, sess, [key]
        )

    def test_get_private_access(self):
        sot = type.Type(**TYPE)

        response = mock.Mock()
        response.status_code = 200
        response.body = {
            "volume_type_access": [{"project_id": "a", "volume_type_id": "b"}]
        }
        response.json = mock.Mock(return_value=response.body)
        self.sess.get = mock.Mock(return_value=response)

        self.assertEqual(
            response.body["volume_type_access"],
            sot.get_private_access(self.sess),
        )

        self.sess.get.assert_called_with(
            f"types/{sot.id}/os-volume-type-access"
        )

    def test_add_private_access(self):
        sot = type.Type(**TYPE)

        self.assertIsNone(sot.add_private_access(self.sess, "a"))

        url = f"types/{sot.id}/action"
        body = {"addProjectAccess": {"project": "a"}}
        self.sess.post.assert_called_with(url, json=body)

    def test_remove_private_access(self):
        sot = type.Type(**TYPE)

        self.assertIsNone(sot.remove_private_access(self.sess, "a"))

        url = f"types/{sot.id}/action"
        body = {"removeProjectAccess": {"project": "a"}}
        self.sess.post.assert_called_with(url, json=body)
