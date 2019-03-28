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

from openstack.object_store.v1 import account


CONTAINER_NAME = "mycontainer"

ACCOUNT_EXAMPLE = {
    'content-length': '0',
    'accept-ranges': 'bytes',
    'date': 'Sat, 05 Jul 2014 19:17:40 GMT',
    'x-account-bytes-used': '12345',
    'x-account-container-count': '678',
    'content-type': 'text/plain; charset=utf-8',
    'x-account-object-count': '98765',
    'x-timestamp': '1453413555.88937'
}


class TestAccount(base.TestCase):

    def setUp(self):
        super(TestAccount, self).setUp()
        self.endpoint = self.cloud.object_store.get_endpoint() + '/'

    def test_basic(self):
        sot = account.Account(**ACCOUNT_EXAMPLE)
        self.assertIsNone(sot.resources_key)
        self.assertIsNone(sot.id)
        self.assertEqual('/', sot.base_path)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_head)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_create)

    def test_make_it(self):
        sot = account.Account(**ACCOUNT_EXAMPLE)
        self.assertIsNone(sot.id)
        self.assertEqual(int(ACCOUNT_EXAMPLE['x-account-bytes-used']),
                         sot.account_bytes_used)
        self.assertEqual(int(ACCOUNT_EXAMPLE['x-account-container-count']),
                         sot.account_container_count)
        self.assertEqual(int(ACCOUNT_EXAMPLE['x-account-object-count']),
                         sot.account_object_count)
        self.assertEqual(ACCOUNT_EXAMPLE['x-timestamp'], sot.timestamp)

    def test_set_temp_url_key(self):
        sot = account.Account()
        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-account-meta-temp-url-key': key})),
            dict(method='HEAD', uri=self.endpoint,
                 headers={
                     'x-account-meta-temp-url-key': key}),
        ])
        sot.set_temp_url_key(self.cloud.object_store, key)
        self.assert_calls()

    def test_set_account_temp_url_key_second(self):
        sot = account.Account()
        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-account-meta-temp-url-key-2': key})),
            dict(method='HEAD', uri=self.endpoint,
                 headers={
                     'x-account-meta-temp-url-key-2': key}),
        ])
        sot.set_temp_url_key(self.cloud.object_store, key, secondary=True)
        self.assert_calls()
