#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from shade import exc
from shade.tests import fakes
from shade.tests.unit import base


class TestKeypair(base.RequestsMockTestCase):

    def setUp(self):
        super(TestKeypair, self).setUp()
        self.keyname = self.getUniqueString('key')
        self.key = fakes.make_fake_keypair(self.keyname)

    def test_create_keypair(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-keypairs']),
                 json={'keypair': self.key},
                 validate=dict(json={
                     'keypair': {
                         'name': self.key['name'],
                         'public_key': self.key['public_key']}})),
        ])

        new_key = self.cloud.create_keypair(
            self.keyname, self.key['public_key'])
        self.assertEqual(new_key, self.cloud._normalize_keypair(self.key))

        self.assert_calls()

    def test_create_keypair_exception(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-keypairs']),
                 status_code=400,
                 validate=dict(json={
                     'keypair': {
                         'name': self.key['name'],
                         'public_key': self.key['public_key']}})),
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_keypair,
            self.keyname, self.key['public_key'])

        self.assert_calls()

    def test_delete_keypair(self):
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-keypairs', self.keyname]),
                 status_code=202),
        ])
        self.assertTrue(self.cloud.delete_keypair(self.keyname))

        self.assert_calls()

    def test_delete_keypair_not_found(self):
        self.register_uris([
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-keypairs', self.keyname]),
                 status_code=404),
        ])
        self.assertFalse(self.cloud.delete_keypair(self.keyname))

        self.assert_calls()

    def test_list_keypairs(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-keypairs']),
                 json={'keypairs': [{'keypair': self.key}]}),

        ])
        keypairs = self.cloud.list_keypairs()
        self.assertEqual(keypairs, self.cloud._normalize_keypairs([self.key]))
        self.assert_calls()

    def test_list_keypairs_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-keypairs']),
                 status_code=400),

        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_keypairs)
        self.assert_calls()
