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

from urllib import parse

from openstack import exceptions
from openstack.object_store.v1 import obj
from openstack.tests.unit import base


class TestPaths(base.TestCase):
    def test_missing_id(self):
        with self.assertRaises(exceptions.InvalidRequest):
            obj.Object(container='container')._prepare_request()

    def test_query_parameters(self):
        request = obj.Object(
            name='/object?#%2F/', container='container?#%2F'
        )._prepare_request(params={'multipart-manifest': 'delete'})
        self.assertEqual(
            '/container%3F%23%252F//object%3F%23%252F/'
            '?multipart-manifest=delete',
            request.url,
        )

    def test_reserved_characters(self):
        proxy = self.cloud.object_store
        endpoint = proxy.get_endpoint()
        assert endpoint is not None
        container = 'container ?#%é'
        name = '/directory/object ?#%2Fé/'
        container_url = endpoint + '/' + parse.quote(container, safe='')
        object_url = container_url + '/' + parse.quote(name, safe='/')
        self.register_uris(
            [
                dict(method='PUT', uri=container_url, status_code=201),
                dict(
                    method='GET',
                    uri=container_url + '?format=json',
                    json=[{'name': name}],
                    complete_qs=True,
                ),
                dict(method='PUT', uri=object_url, status_code=201),
                dict(method='HEAD', uri=object_url, status_code=200),
                dict(method='GET', uri=object_url, content=b'content'),
                dict(method='DELETE', uri=object_url, status_code=204),
                dict(method='DELETE', uri=container_url, status_code=204),
            ]
        )
        proxy.create_container(container)
        listed = list(proxy.objects(container, paginated=False))
        self.assertEqual(name, listed[0].name)
        self.assertEqual(container, listed[0].container)
        proxy.create_object(container, name, data=b'content')
        proxy.get_object_metadata(listed[0])
        self.assertEqual(
            b'content',
            b''.join(proxy.stream_object(name, container=container)),
        )
        proxy.delete_object(
            obj.Object(
                id=name,
                container=container,
                is_static_large_object=False,
            ),
            ignore_missing=False,
        )
        proxy.delete_container(container, ignore_missing=False)
        self.assert_calls()
