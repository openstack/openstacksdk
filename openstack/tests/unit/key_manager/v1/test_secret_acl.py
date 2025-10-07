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

from openstack.key_manager.v1 import secret_acl
from openstack.tests.unit import base


PUT_PATCH_EXAMPLE = {"acl_ref": "https://barbican/v1/secrets/UUID/acl"}
GET_EXAMPLE = {
    "read": {
        "updated": "2015-05-12T20:08:47.644264",
        "created": "2015-05-12T19:23:44.019168",
        "users": ["u1", "u2"],
        "project-access": True,
    }
}


class TestSecretACL(base.TestCase):
    def test_basic(self):
        sot = secret_acl.SecretACL(secret_id="SID")
        self.assertEqual('/secrets/%(secret_id)s/acl', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        # GET-shape payload
        sot = secret_acl.SecretACL(**GET_EXAMPLE)
        self.assertIn("project-access", sot.read)
        self.assertEqual(["u1", "u2"], sot.read["users"])

        # PUT/PATCH-shape payload
        sot = secret_acl.SecretACL(**PUT_PATCH_EXAMPLE)
        self.assertEqual(PUT_PATCH_EXAMPLE["acl_ref"], sot.acl_ref)
