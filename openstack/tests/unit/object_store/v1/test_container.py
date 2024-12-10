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

import json

from openstack.object_store.v1 import container
from openstack.tests.unit import base


class TestContainer(base.TestCase):
    def setUp(self):
        super().setUp()
        self.container = self.getUniqueString()
        self.endpoint = self.cloud.object_store.get_endpoint() + '/'
        self.container_endpoint = f'{self.endpoint}{self.container}'

        self.body = {
            "count": 2,
            "bytes": 630666,
            "name": self.container,
        }

        self.headers = {
            'x-container-object-count': '2',
            'x-container-read': 'read-settings',
            'x-container-write': 'write-settings',
            'x-container-sync-to': 'sync-to',
            'x-container-sync-key': 'sync-key',
            'x-container-bytes-used': '630666',
            'x-versions-location': 'versions-location',
            'x-history-location': 'history-location',
            'content-type': 'application/json; charset=utf-8',
            'x-timestamp': '1453414055.48672',
            'x-storage-policy': 'Gold',
        }
        self.body_plus_headers = dict(self.body, **self.headers)

    def test_basic(self):
        sot = container.Container.new(**self.body)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('name', sot._alternate_id())
        self.assertEqual('/', sot.base_path)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_head)
        self.assert_no_calls()

    def test_make_it(self):
        sot = container.Container.new(**self.body)
        self.assertEqual(self.body['name'], sot.id)
        self.assertEqual(self.body['name'], sot.name)
        self.assertEqual(self.body['count'], sot.count)
        self.assertEqual(self.body['count'], sot.object_count)
        self.assertEqual(self.body['bytes'], sot.bytes)
        self.assertEqual(self.body['bytes'], sot.bytes_used)
        self.assert_no_calls()

    def test_create_and_head(self):
        sot = container.Container(**self.body_plus_headers)

        # Attributes from create
        self.assertEqual(self.body_plus_headers['name'], sot.id)
        self.assertEqual(self.body_plus_headers['name'], sot.name)
        self.assertEqual(self.body_plus_headers['count'], sot.count)
        self.assertEqual(self.body_plus_headers['bytes'], sot.bytes)

        # Attributes from header
        self.assertEqual(
            int(self.body_plus_headers['x-container-object-count']),
            sot.object_count,
        )
        self.assertEqual(
            int(self.body_plus_headers['x-container-bytes-used']),
            sot.bytes_used,
        )
        self.assertEqual(
            self.body_plus_headers['x-container-read'], sot.read_ACL
        )
        self.assertEqual(
            self.body_plus_headers['x-container-write'], sot.write_ACL
        )
        self.assertEqual(
            self.body_plus_headers['x-container-sync-to'], sot.sync_to
        )
        self.assertEqual(
            self.body_plus_headers['x-container-sync-key'], sot.sync_key
        )
        self.assertEqual(
            self.body_plus_headers['x-versions-location'],
            sot.versions_location,
        )
        self.assertEqual(
            self.body_plus_headers['x-history-location'], sot.history_location
        )
        self.assertEqual(self.body_plus_headers['x-timestamp'], sot.timestamp)
        self.assertEqual(
            self.body_plus_headers['x-storage-policy'], sot.storage_policy
        )

    def test_list(self):
        containers = [
            {"count": 999, "bytes": 12345, "name": "container1"},
            {"count": 888, "bytes": 54321, "name": "container2"},
        ]
        self.register_uris(
            [dict(method='GET', uri=self.endpoint, json=containers)]
        )

        response = container.Container.list(self.cloud.object_store)

        self.assertEqual(len(containers), len(list(response)))
        for index, item in enumerate(response):
            self.assertEqual(container.Container, type(item))
            self.assertEqual(containers[index]["name"], item.name)
            self.assertEqual(containers[index]["count"], item.count)
            self.assertEqual(containers[index]["bytes"], item.bytes)

        self.assert_calls()

    def _test_create_update(self, sot, sot_call, sess_method):
        sot.read_ACL = "some ACL"
        sot.write_ACL = "another ACL"
        sot.is_content_type_detected = True
        headers = {
            "x-container-read": "some ACL",
            "x-container-write": "another ACL",
            "x-detect-content-type": 'True',
            "X-Container-Meta-foo": "bar",
        }
        self.register_uris(
            [
                dict(
                    method=sess_method,
                    uri=self.container_endpoint,
                    json=self.body,
                    validate=dict(headers=headers),
                ),
            ]
        )
        sot_call(self.cloud.object_store)

        self.assert_calls()

    def test_create(self):
        sot = container.Container.new(
            name=self.container, metadata={'foo': 'bar'}
        )
        self._test_create_update(sot, sot.create, 'PUT')

    def test_commit(self):
        sot = container.Container.new(
            name=self.container, metadata={'foo': 'bar'}
        )
        self._test_create_update(sot, sot.commit, 'POST')

    def test_to_dict_recursion(self):
        # This test is verifying that circular aliases in a Resource
        # do not cause infinite recursion. count is aliased to object_count
        # and object_count is aliased to count.
        sot = container.Container.new(name=self.container)
        sot_dict = sot.to_dict()
        self.assertIsNone(sot_dict['count'])
        self.assertIsNone(sot_dict['object_count'])
        self.assertEqual(sot_dict['id'], self.container)
        self.assertEqual(sot_dict['name'], self.container)

    def test_to_json(self):
        sot = container.Container.new(name=self.container)
        self.assertEqual(
            {
                'bytes': None,
                'bytes_used': None,
                'content_type': None,
                'count': None,
                'id': self.container,
                'if_none_match': None,
                'is_content_type_detected': None,
                'is_newest': None,
                'location': None,
                'name': self.container,
                'object_count': None,
                'read_ACL': None,
                'sync_key': None,
                'sync_to': None,
                'meta_temp_url_key': None,
                'meta_temp_url_key_2': None,
                'timestamp': None,
                'versions_location': None,
                'history_location': None,
                'write_ACL': None,
                'storage_policy': None,
            },
            json.loads(json.dumps(sot)),
        )

    def _test_no_headers(self, sot, sot_call, sess_method):
        headers = {}
        self.register_uris(
            [
                dict(
                    method=sess_method,
                    uri=self.container_endpoint,
                    validate=dict(headers=headers),
                )
            ]
        )
        sot_call(self.cloud.object_store)

    def test_create_no_headers(self):
        sot = container.Container.new(name=self.container)
        self._test_no_headers(sot, sot.create, 'PUT')
        self.assert_calls()

    def test_commit_no_headers(self):
        sot = container.Container.new(name=self.container)
        self._test_no_headers(sot, sot.commit, 'POST')
        self.assert_calls()

    def test_set_temp_url_key(self):
        sot = container.Container.new(name=self.container)
        key = self.getUniqueString()

        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.container_endpoint,
                    status_code=204,
                    validate=dict(
                        headers={'x-container-meta-temp-url-key': key}
                    ),
                ),
                dict(
                    method='HEAD',
                    uri=self.container_endpoint,
                    headers={'x-container-meta-temp-url-key': key},
                ),
            ]
        )
        sot.set_temp_url_key(self.cloud.object_store, key)
        self.assert_calls()

    def test_set_temp_url_key_second(self):
        sot = container.Container.new(name=self.container)
        key = self.getUniqueString()

        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.container_endpoint,
                    status_code=204,
                    validate=dict(
                        headers={'x-container-meta-temp-url-key-2': key}
                    ),
                ),
                dict(
                    method='HEAD',
                    uri=self.container_endpoint,
                    headers={'x-container-meta-temp-url-key-2': key},
                ),
            ]
        )
        sot.set_temp_url_key(self.cloud.object_store, key, secondary=True)
        self.assert_calls()
