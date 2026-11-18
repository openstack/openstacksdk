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

from openstack import exceptions
from openstack.tests.unit import base


class TestListing(base.TestCase):
    def setUp(self):
        super().setUp()
        self.proxy = self.cloud.object_store
        endpoint = self.proxy.get_endpoint()
        assert endpoint is not None
        self.endpoint = endpoint.rstrip('/')

    def test_containers_paginated(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.endpoint + '/?format=json',
                    json=[{'name': 'first'}, {'name': 'second'}],
                    headers={'X-Account-Container-Count': '2'},
                    complete_qs=True,
                ),
                dict(
                    method='GET',
                    uri=self.endpoint + '/?format=json&marker=second',
                    json=[{'name': 'third'}],
                    complete_qs=True,
                ),
                dict(
                    method='GET',
                    uri=self.endpoint + '/?format=json&marker=third',
                    json=[],
                    complete_qs=True,
                ),
            ]
        )
        self.assertEqual(
            ['first', 'second', 'third'],
            [c.name for c in self.proxy.containers()],
        )
        self.assert_calls()

    def test_containers_one_page(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.endpoint + '/?format=json&end_marker=z&limit=1',
                    json=[{'name': 'first'}],
                    headers={'X-Account-Container-Count': '100'},
                    complete_qs=True,
                ),
            ]
        )
        self.assertEqual(
            ['first'],
            [
                c.name
                for c in self.proxy.containers(
                    paginated=False, end_marker='z', limit=1
                )
            ],
        )
        self.assert_calls()

    def test_objects_delimiter_paginated(self):
        query = '?format=json&delimiter=%2F&prefix=a&end_marker=z&limit=1'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.endpoint + '/container' + query,
                    json=[{'subdir': 'a/'}],
                    headers={'X-Container-Object-Count': '1'},
                    complete_qs=True,
                ),
                dict(
                    method='GET',
                    uri=self.endpoint + '/container' + query + '&marker=a%2F',
                    json=[{'name': 'another'}],
                    complete_qs=True,
                ),
                dict(
                    method='GET',
                    uri=self.endpoint
                    + '/container'
                    + query
                    + '&marker=another',
                    json=[],
                    complete_qs=True,
                ),
            ]
        )
        objects = list(
            self.proxy.objects(
                'container', delimiter='/', prefix='a', end_marker='z', limit=1
            )
        )
        self.assertEqual(['a/', 'another'], [o.name for o in objects])
        self.assertEqual('a/', objects[0].subdir)
        self.assertEqual(['a/', 'another'], [o.id for o in objects])
        self.assertTrue(all(o.container == 'container' for o in objects))
        self.assert_calls()

    def test_objects_one_page(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.endpoint + '/container?format=json',
                    json=[{'name': 'first'}],
                    headers={'X-Container-Object-Count': '100'},
                    complete_qs=True,
                ),
            ]
        )
        self.assertEqual(
            ['first'],
            [o.name for o in self.proxy.objects('container', paginated=False)],
        )
        self.assert_calls()

    def test_objects_repeated_marker(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.endpoint + '/container?format=json&marker=first',
                    json=[{'name': 'first'}],
                    complete_qs=True,
                ),
            ]
        )
        with self.assertRaisesRegex(
            exceptions.SDKException, 'Endless pagination loop'
        ):
            list(self.proxy.objects('container', marker='first'))
        self.assert_calls()

    def test_objects_path_filter(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.endpoint + '/container?format=json&path=dir',
                    json=[{'name': 'dir/object'}],
                    complete_qs=True,
                ),
            ]
        )
        self.assertEqual(
            ['dir/object'],
            [
                o.name
                for o in self.proxy.objects(
                    'container', path='dir', paginated=False
                )
            ],
        )
        self.assert_calls()

    def test_objects_empty(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.endpoint + '/container?format=json',
                    json=[],
                    complete_qs=True,
                ),
            ]
        )
        self.assertEqual([], list(self.proxy.objects('container')))
        self.assert_calls()
