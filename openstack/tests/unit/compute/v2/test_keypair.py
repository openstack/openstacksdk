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

from openstack.compute.v2 import keypair

EXAMPLE = {
    'fingerprint': '1',
    'name': '2',
    'public_key': '3',
    'private_key': '3',
}


class TestKeypair(base.TestCase):

    def test_basic(self):
        sot = keypair.Keypair()
        self.assertEqual('keypair', sot.resource_key)
        self.assertEqual('keypairs', sot.resources_key)
        self.assertEqual('/os-keypairs', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = keypair.Keypair(**EXAMPLE)
        self.assertEqual(EXAMPLE['fingerprint'], sot.fingerprint)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['public_key'], sot.public_key)
        self.assertEqual(EXAMPLE['private_key'], sot.private_key)
