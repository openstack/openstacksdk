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

import io

from openstack.tests.unit import base


class TestCreate(base.TestCase):
    def test_create_object_stream(self):
        proxy = self.cloud.object_store
        endpoint = proxy.get_endpoint()
        assert endpoint is not None
        self.register_uris(
            [
                dict(
                    method='PUT',
                    uri=endpoint + '/container/directory/object',
                    status_code=201,
                    headers={'Etag': 'checksum', 'X-Trans-Id': 'transaction'},
                    validate=dict(data=b'file content'),
                ),
            ]
        )
        with io.BytesIO(b'file content') as stream:
            obj = proxy.create_object(
                'container',
                'directory/object',
                data=stream,
                generate_checksums=False,
            )
            self.assertFalse(stream.closed)
        assert obj is not None
        self.assertEqual('directory/object', obj.name)
        self.assertEqual('container', obj.container)
        self.assertEqual('checksum', obj.etag)
        self.assertEqual('transaction', obj.transaction_id)
        self.assert_calls()

    def test_create_container_transaction(self):
        proxy = self.cloud.object_store
        endpoint = proxy.get_endpoint()
        assert endpoint is not None
        self.register_uris(
            [
                dict(
                    method='PUT',
                    uri=endpoint + '/container',
                    status_code=201,
                    headers={'X-Trans-Id': 'transaction'},
                ),
            ]
        )
        container = proxy.create_container('container')
        self.assertEqual('container', container.name)
        self.assertEqual('transaction', container.transaction_id)
        self.assert_calls()
