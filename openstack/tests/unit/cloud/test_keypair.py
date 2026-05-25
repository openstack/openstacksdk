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

import datetime

import fixtures

from openstack import exceptions
from openstack.tests.unit import base

FAKE_PUBLIC_KEY = (
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCkF3MX59OrlBs3dH5CU7lNmvpbrgZxSpyGj"
    "lnE8Flkirnc/Up22lpjznoxqeoTAwTW034k7Dz6aYIrZGmQwe2TkE084yqvlj45Dkyoj95fW/"
    "sZacm0cZNuL69EObEGHdprfGJQajrpz22NQoCD8TFB8Wv+8om9NH9Le6s+WPe98WC77KLw8qg"
    "fQsbIey+JawPWl4O67ZdL5xrypuRjfIPWjgy/VH85IXg/Z/GONZ2nxHgSShMkwqSFECAC5L3P"
    "HB+0+/12M/iikdatFSVGjpuHvkLOs3oe7m6HlOfluSJ85BzLWBbvva93qkGmLg4ZAc8rPh2O+"
    "YIsBUHNLLMM/oQp Generated-by-Nova\n"
)


def make_fake_keypair(name):
    # Note: this is literally taken from:
    # https://docs.openstack.org/api-ref/compute/
    return {
        "fingerprint": "7e:eb:ab:24:ba:d1:e1:88:ae:9a:fb:66:53:df:d3:bd",
        "name": name,
        "type": "ssh",
        "public_key": FAKE_PUBLIC_KEY,
        "created_at": datetime.datetime.now().isoformat(),
    }


class TestKeypair(base.TestCase):
    def setUp(self):
        super().setUp()
        self.keyname = self.getUniqueString('key')
        self.key = make_fake_keypair(self.keyname)
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
