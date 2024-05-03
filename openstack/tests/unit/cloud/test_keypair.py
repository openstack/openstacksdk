#
# Licensed under the Apache License, Version 2.0 (the "License");
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

import fixtures

from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestKeypair(base.TestCase):
    def setUp(self):
        super().setUp()
        self.keyname = self.getUniqueString('key')
        self.key = fakes.make_fake_keypair(self.keyname)
        self.useFixture(
            fixtures.MonkeyPatch(
                'openstack.utils.maximum_supported_microversion',
                lambda *args, **kwargs: '2.10',
            )
        )

    def test_create_keypair(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['os-keypairs']
                    ),
                    json={'keypair': self.key},
                    validate=dict(
                        json={
                            'keypair': {
                                'name': self.key['name'],
                                'public_key': self.key['public_key'],
                            }
                        }
                    ),
                ),
            ]
        )

        new_key = self.cloud.create_keypair(
            self.keyname, self.key['public_key']
        )
        new_key_cmp = new_key.to_dict(ignore_none=True)
        new_key_cmp.pop('location')
        new_key_cmp.pop('id')
        self.assertEqual(new_key_cmp, self.key)

        self.assert_calls()

    def test_create_keypair_exception(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['os-keypairs']
                    ),
                    status_code=400,
                    validate=dict(
                        json={
                            'keypair': {
                                'name': self.key['name'],
                                'public_key': self.key['public_key'],
                            }
                        }
                    ),
                ),
            ]
        )

        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_keypair,
            self.keyname,
            self.key['public_key'],
        )

        self.assert_calls()

    def test_delete_keypair(self):
        self.register_uris(
            [
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['os-keypairs', self.keyname],
                    ),
                    status_code=202,
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_keypair(self.keyname))

        self.assert_calls()

    def test_delete_keypair_not_found(self):
        self.register_uris(
            [
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['os-keypairs', self.keyname],
                    ),
                    status_code=404,
                ),
            ]
        )
        self.assertFalse(self.cloud.delete_keypair(self.keyname))

        self.assert_calls()

    def test_list_keypairs(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['os-keypairs']
                    ),
                    json={'keypairs': [{'keypair': self.key}]},
                ),
            ]
        )
        keypairs = self.cloud.list_keypairs()
        self.assertEqual(len(keypairs), 1)
        self.assertEqual(keypairs[0].name, self.key['name'])
        self.assert_calls()

    def test_list_keypairs_empty_filters(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['os-keypairs']
                    ),
                    json={'keypairs': [{'keypair': self.key}]},
                ),
            ]
        )
        keypairs = self.cloud.list_keypairs(filters=None)
        self.assertEqual(len(keypairs), 1)
        self.assertEqual(keypairs[0].name, self.key['name'])
        self.assert_calls()

    def test_list_keypairs_notempty_filters(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['os-keypairs'],
                        qs_elements=['user_id=b'],
                    ),
                    json={'keypairs': [{'keypair': self.key}]},
                ),
            ]
        )
        keypairs = self.cloud.list_keypairs(
            filters={'user_id': 'b', 'fake': 'dummy'}
        )
        self.assertEqual(len(keypairs), 1)
        self.assertEqual(keypairs[0].name, self.key['name'])
        self.assert_calls()

    def test_list_keypairs_exception(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['os-keypairs']
                    ),
                    status_code=400,
                ),
            ]
        )
        self.assertRaises(exceptions.SDKException, self.cloud.list_keypairs)
        self.assert_calls()
