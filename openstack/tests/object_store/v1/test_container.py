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

from openstack.object_store.v1 import container


ACCOUNT_EXAMPLE = {
    'content-length': '0',
    'accept-ranges': 'bytes',
    'x-timestamp': '1403312946.78273',
    'id': 'tx4272aa0d6e1e4f8f971f8-0053b84f54',
    'date': 'Sat, 05 Jul 2014 19:17:40 GMT',
    'x-account-bytes-used': '12345',
    'x-account-container-count': '678',
    'content-type': 'text/plain; charset=utf-8',
    'x-account-object-count': '98765'
}

CONT_EXAMPLE = {
    "count": 999,
    "bytes": 12345,
    "name": "mycontainer"
}

HEAD_EXAMPLE = {
    'content-length': '346',
    'x-container-object-count': '2',
    'accept-ranges': 'bytes',
    'id': 'tx1878fdc50f9b4978a3fdc-0053c31462',
    'date': 'Sun, 13 Jul 2014 23:21:06 GMT',
    'x-timestamp': '1403312946.79252',
    'x-container-read': 'read-settings',
    'x-container-write': 'write-settings',
    'x-container-sync-to': 'sync-to',
    'x-container-sync-key': 'sync-key',
    'x-container-bytes-used': '630666',
    'x-versions-location': 'versions-location',
    'content-type': 'application/json; charset=utf-8'
}

LIST_EXAMPLE = [
    {
        "count": 999,
        "bytes": 12345,
        "name": "container1"
    },
    {
        "count": 888,
        "bytes": 54321,
        "name": "container2"
    }
]


class TestAccount(testtools.TestCase):

    def test_make_it(self):
        sot = container.Container(ACCOUNT_EXAMPLE)
        self.assertIsNone(sot.id)
        self.assertEqual(ACCOUNT_EXAMPLE['x-timestamp'], sot.timestamp)
        self.assertEqual(ACCOUNT_EXAMPLE['x-account-bytes-used'],
                         sot.account_bytes_used)
        self.assertEqual(ACCOUNT_EXAMPLE['x-account-container-count'],
                         sot.account_container_count)
        self.assertEqual(ACCOUNT_EXAMPLE['x-account-object-count'],
                         sot.account_object_count)


class TestContainer(testtools.TestCase):

    def test_basic(self):
        sot = container.Container(CONT_EXAMPLE)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/', sot.base_path)
        self.assertEqual('object-store', sot.service.service_type)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_head)

    def test_make_it(self):
        sot = container.Container(CONT_EXAMPLE)
        self.assertEqual(CONT_EXAMPLE['name'], sot.id)
        self.assertEqual(CONT_EXAMPLE['name'], sot.name)
        self.assertEqual(CONT_EXAMPLE['count'], sot.count)
        self.assertEqual(CONT_EXAMPLE['bytes'], sot.bytes)

    def test_create_and_head(self):
        sot = container.Container(CONT_EXAMPLE)

        # Update container with HEAD data
        sot._attrs.update(HEAD_EXAMPLE)

        # Attributes from create
        self.assertEqual(CONT_EXAMPLE['name'], sot.id)
        self.assertEqual(CONT_EXAMPLE['name'], sot.name)
        self.assertEqual(CONT_EXAMPLE['count'], sot.count)
        self.assertEqual(CONT_EXAMPLE['bytes'], sot.bytes)

        # Attributes from header
        self.assertEqual(HEAD_EXAMPLE['x-container-object-count'],
                         sot.object_count)
        self.assertEqual(HEAD_EXAMPLE['x-container-bytes-used'],
                         sot.bytes_used)
        self.assertEqual(HEAD_EXAMPLE['x-container-read'],
                         sot.can_read)
        self.assertEqual(HEAD_EXAMPLE['x-container-write'],
                         sot.can_write)
        self.assertEqual(HEAD_EXAMPLE['x-container-sync-to'],
                         sot.sync_to)
        self.assertEqual(HEAD_EXAMPLE['x-container-sync-key'],
                         sot.sync_key)
        self.assertEqual(HEAD_EXAMPLE['x-versions-location'],
                         sot.versions_location)

    @mock.patch("openstack.resource.Resource.list")
    def test_list(self, fake_list):
        fake_val = [container.Container.existing(**ex) for ex in LIST_EXAMPLE]
        fake_list.return_value = fake_val

        # Since the list method is mocked out, just pass None for the session.
        response = container.Container.list(None)

        self.assertTrue(len(response), len(LIST_EXAMPLE))
        for item in range(len(response)):
            self.assertEqual(type(response[item]), container.Container)
            self.assertEqual(response[item].name, LIST_EXAMPLE[item]["name"])
            self.assertEqual(response[item].count, LIST_EXAMPLE[item]["count"])
            self.assertEqual(response[item].bytes, LIST_EXAMPLE[item]["bytes"])
