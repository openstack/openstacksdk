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

import mock
import testtools

from openstack.compute.v2 import keypair
from openstack import exceptions

EXAMPLE = {
    'keypair': {
        'fingerprint': '1',
        'name': '2',
        'public_key': '3',
    }
}


class TestKeypair(testtools.TestCase):

    def test_basic(self):
        sot = keypair.Keypair()
        self.assertEqual('keypair', sot.resource_key)
        self.assertEqual('keypairs', sot.resources_key)
        self.assertEqual('/os-keypairs', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = keypair.Keypair(EXAMPLE)
        self.assertEqual(EXAMPLE['keypair']['fingerprint'], sot.fingerprint)
        self.assertEqual(EXAMPLE['keypair']['name'], sot.name)
        self.assertEqual(EXAMPLE['keypair']['public_key'], sot.public_key)

    def test_find(self):
        resp = mock.Mock()
        resp.body = EXAMPLE
        sess = mock.Mock()
        sess.get = mock.MagicMock()
        sess.get.return_value = resp
        sot = keypair.Keypair()
        result = sot.find(sess, "kato")
        url = 'os-keypairs/kato'
        sess.get.assert_called_with(url, service=sot.service)
        self.assertEqual(EXAMPLE['keypair']['fingerprint'], result.fingerprint)
        self.assertEqual(EXAMPLE['keypair']['name'], result.name)
        self.assertEqual(EXAMPLE['keypair']['public_key'], result.public_key)

    def test_find_not_found(self):
        sess = mock.Mock()
        sess.get = mock.MagicMock()
        sess.get.side_effect = exceptions.HttpException("404")
        sot = keypair.Keypair()
        self.assertEqual(None, sot.find(sess, "kato"))
