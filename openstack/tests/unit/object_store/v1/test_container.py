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

from datetime import datetime
import iso8601

import mock
import testtools

from openstack.object_store.v1 import container


CONTAINER_NAME = "mycontainer"

CONT_EXAMPLE = {
    "count": 999,
    "bytes": 12345,
    "name": CONTAINER_NAME
}

HEAD_EXAMPLE = {
    'content-length': '346',
    'x-container-object-count': '2',
    'accept-ranges': 'bytes',
    'id': 'tx1878fdc50f9b4978a3fdc-0053c31462',
    'date': 'Sun, 13 Jul 2014 23:21:06 GMT',
    'x-container-read': 'read-settings',
    'x-container-write': 'write-settings',
    'x-container-sync-to': 'sync-to',
    'x-container-sync-key': 'sync-key',
    'x-container-bytes-used': '630666',
    'x-versions-location': 'versions-location',
    'content-type': 'application/json; charset=utf-8',
    'x-timestamp': '1453414055.48672'
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


class TestContainer(testtools.TestCase):

    def setUp(self):
        super(TestContainer, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = {}
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.headers = {"X-Trans-Id": "abcdef"}
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)
        self.sess.post = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = container.Container.new(**CONT_EXAMPLE)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('name', sot.id_attribute)
        self.assertEqual('/', sot.base_path)
        self.assertEqual('object-store', sot.service.service_type)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_head)

    def test_make_it(self):
        sot = container.Container.new(**CONT_EXAMPLE)
        self.assertEqual(CONT_EXAMPLE['name'], sot.id)
        self.assertEqual(CONT_EXAMPLE['name'], sot.name)
        self.assertEqual(CONT_EXAMPLE['count'], sot.count)
        self.assertEqual(CONT_EXAMPLE['bytes'], sot.bytes)

    def test_create_and_head(self):
        sot = container.Container(CONT_EXAMPLE)

        # Update container with HEAD data
        sot._attrs.update({'headers': HEAD_EXAMPLE})

        # Attributes from create
        self.assertEqual(CONT_EXAMPLE['name'], sot.id)
        self.assertEqual(CONT_EXAMPLE['name'], sot.name)
        self.assertEqual(CONT_EXAMPLE['count'], sot.count)
        self.assertEqual(CONT_EXAMPLE['bytes'], sot.bytes)

        # Attributes from header
        self.assertEqual(int(HEAD_EXAMPLE['x-container-object-count']),
                         sot.object_count)
        self.assertEqual(int(HEAD_EXAMPLE['x-container-bytes-used']),
                         sot.bytes_used)
        self.assertEqual(HEAD_EXAMPLE['x-container-read'],
                         sot.read_ACL)
        self.assertEqual(HEAD_EXAMPLE['x-container-write'],
                         sot.write_ACL)
        self.assertEqual(HEAD_EXAMPLE['x-container-sync-to'],
                         sot.sync_to)
        self.assertEqual(HEAD_EXAMPLE['x-container-sync-key'],
                         sot.sync_key)
        self.assertEqual(HEAD_EXAMPLE['x-versions-location'],
                         sot.versions_location)
        self.assertEqual(datetime(2016, 1, 21, 22, 7, 35, 486720,
                                  tzinfo=iso8601.UTC),
                         sot.timestamp)

    @mock.patch("openstack.resource.Resource.list")
    def test_list(self, fake_list):
        fake_val = [container.Container.existing(**ex) for ex in LIST_EXAMPLE]
        fake_list.return_value = fake_val

        # Since the list method is mocked out, just pass None for the session.
        response = container.Container.list(None)

        self.assertEqual(len(LIST_EXAMPLE), len(response))
        for item in range(len(response)):
            self.assertEqual(container.Container, type(response[item]))
            self.assertEqual(LIST_EXAMPLE[item]["name"], response[item].name)
            self.assertEqual(LIST_EXAMPLE[item]["count"], response[item].count)
            self.assertEqual(LIST_EXAMPLE[item]["bytes"], response[item].bytes)

    def _test_create_update(self, sot, sot_call, sess_method):
        sot.read_ACL = "some ACL"
        sot.write_ACL = "another ACL"
        sot.is_content_type_detected = True
        headers = {
            "x-container-read": "some ACL",
            "x-container-write": "another ACL",
            "x-detect-content-type": True,
            "Accept": "",
        }
        sot_call(self.sess)

        url = "/%s" % CONTAINER_NAME
        sess_method.assert_called_with(url, endpoint_filter=sot.service,
                                       headers=headers)

    def test_create(self):
        sot = container.Container.new(name=CONTAINER_NAME)
        self._test_create_update(sot, sot.create, self.sess.put)

    def test_update(self):
        sot = container.Container.new(name=CONTAINER_NAME)
        self._test_create_update(sot, sot.update, self.sess.post)

    def _test_no_headers(self, sot, sot_call, sess_method):
        sot = container.Container.new(name=CONTAINER_NAME)
        sot.create(self.sess)
        url = "/%s" % CONTAINER_NAME
        headers = {'Accept': ''}
        self.sess.put.assert_called_with(url, endpoint_filter=sot.service,
                                         headers=headers)

    def test_create_no_headers(self):
        sot = container.Container.new(name=CONTAINER_NAME)
        self._test_no_headers(sot, sot.create, self.sess.put)

    def test_update_no_headers(self):
        sot = container.Container.new(name=CONTAINER_NAME)
        self._test_no_headers(sot, sot.update, self.sess.post)
