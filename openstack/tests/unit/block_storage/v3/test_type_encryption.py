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

from openstack.tests.unit import base

from openstack.block_storage.v3 import type

FAKE_ID = "479394ab-2f25-416e-8f58-721d8e5e29de"
TYPE_ID = "22373aed-c4a8-4072-b66c-bf0a90dc9a12"
TYPE_ENC = {
    "key_size": 256,
    "volume_type_id": TYPE_ID,
    "encryption_id": FAKE_ID,
    "provider": "nova.volume.encryptors.luks.LuksEncryptor",
    "control_location": "front-end",
    "cipher": "aes-xts-plain64",
    "deleted": False,
    "created_at": "2020-10-07T07:52:30.000000",
    "updated_at": "2020-10-08T07:42:45.000000",
    "deleted_at": None,
}


class TestTypeEncryption(base.TestCase):

    def test_basic(self):
        sot = type.TypeEncryption(**TYPE_ENC)
        self.assertEqual("encryption", sot.resource_key)
        self.assertEqual("encryption", sot.resources_key)
        self.assertEqual("/types/%(volume_type_id)s/encryption", sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertTrue(sot.allow_commit)

    def test_new(self):
        sot = type.TypeEncryption.new(encryption_id=FAKE_ID)
        self.assertEqual(FAKE_ID, sot.encryption_id)

    def test_create(self):
        sot = type.TypeEncryption(**TYPE_ENC)
        self.assertEqual(TYPE_ENC["volume_type_id"], sot.volume_type_id)
        self.assertEqual(TYPE_ENC["encryption_id"], sot.encryption_id)
        self.assertEqual(TYPE_ENC["key_size"], sot.key_size)
        self.assertEqual(TYPE_ENC["provider"], sot.provider)
        self.assertEqual(TYPE_ENC["control_location"], sot.control_location)
        self.assertEqual(TYPE_ENC["cipher"], sot.cipher)
        self.assertEqual(TYPE_ENC["deleted"], sot.deleted)
        self.assertEqual(TYPE_ENC["created_at"], sot.created_at)
        self.assertEqual(TYPE_ENC["updated_at"], sot.updated_at)
        self.assertEqual(TYPE_ENC["deleted_at"], sot.deleted_at)
