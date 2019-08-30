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
from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

import random
import string
import tempfile

from openstack.object_store.v1 import account
from openstack.object_store.v1 import container
from openstack.object_store.v1 import obj
from openstack.tests.unit.cloud import test_object as base_test_object
from openstack.tests.unit import test_proxy_base


class TestObjectStoreProxy(test_proxy_base.TestProxyBase):

    kwargs_to_path_args = False

    def setUp(self):
        super(TestObjectStoreProxy, self).setUp()
        self.proxy = self.cloud.object_store
        self.container = self.getUniqueString()
        self.endpoint = self.cloud.object_store.get_endpoint() + '/'
        self.container_endpoint = '{endpoint}{container}'.format(
            endpoint=self.endpoint, container=self.container)

    def test_account_metadata_get(self):
        self.verify_head(self.proxy.get_account_metadata, account.Account)

    def test_container_metadata_get(self):
        self.verify_head(self.proxy.get_container_metadata,
                         container.Container, value="container")

    def test_container_delete(self):
        self.verify_delete(self.proxy.delete_container,
                           container.Container, False)

    def test_container_delete_ignore(self):
        self.verify_delete(self.proxy.delete_container,
                           container.Container, True)

    def test_container_create_attrs(self):
        self.verify_create(
            self.proxy.create_container,
            container.Container,
            method_args=['container_name'],
            expected_kwargs={'name': 'container_name', "x": 1, "y": 2, "z": 3})

    def test_object_metadata_get(self):
        self._verify2("openstack.proxy.Proxy._head",
                      self.proxy.get_object_metadata,
                      method_args=['object'],
                      method_kwargs={'container': 'container'},
                      expected_args=[obj.Object, 'object'],
                      expected_kwargs={'container': 'container'})

    def _test_object_delete(self, ignore):
        expected_kwargs = {
            "ignore_missing": ignore,
            "container": "name",
        }

        self._verify2("openstack.proxy.Proxy._delete",
                      self.proxy.delete_object,
                      method_args=["resource"],
                      method_kwargs=expected_kwargs,
                      expected_args=[obj.Object, "resource"],
                      expected_kwargs=expected_kwargs)

    def test_object_delete(self):
        self._test_object_delete(False)

    def test_object_delete_ignore(self):
        self._test_object_delete(True)

    def test_object_create_attrs(self):
        kwargs = {"name": "test", "data": "data", "container": "name"}

        self._verify2("openstack.proxy.Proxy._create",
                      self.proxy.upload_object,
                      method_kwargs=kwargs,
                      expected_args=[obj.Object],
                      expected_kwargs=kwargs)

    def test_object_create_no_container(self):
        self.assertRaises(TypeError, self.proxy.upload_object)

    def test_object_get(self):
        kwargs = dict(container="container")
        self.verify_get(
            self.proxy.get_object, obj.Object,
            value=["object"],
            method_kwargs=kwargs,
            expected_kwargs=kwargs)

    def test_set_temp_url_key(self):

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
        self.proxy.set_account_temp_url_key(key)
        self.assert_calls()

    def test_set_account_temp_url_key_second(self):

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
        self.proxy.set_account_temp_url_key(key, secondary=True)
        self.assert_calls()

    def test_set_container_temp_url_key(self):

        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-container-meta-temp-url-key': key})),
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'x-container-meta-temp-url-key': key}),
        ])
        self.proxy.set_container_temp_url_key(self.container, key)
        self.assert_calls()

    def test_set_container_temp_url_key_second(self):

        key = 'super-secure-key'

        self.register_uris([
            dict(method='POST', uri=self.container_endpoint,
                 status_code=204,
                 validate=dict(
                     headers={
                         'x-container-meta-temp-url-key-2': key})),
            dict(method='HEAD', uri=self.container_endpoint,
                 headers={
                     'x-container-meta-temp-url-key-2': key}),
        ])
        self.proxy.set_container_temp_url_key(
            self.container, key, secondary=True)
        self.assert_calls()

    def test_copy_object(self):
        self.assertRaises(NotImplementedError, self.proxy.copy_object)

    def test_file_segment(self):
        file_size = 4200
        content = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits)
            for _ in range(file_size)).encode('latin-1')
        self.imagefile = tempfile.NamedTemporaryFile(delete=False)
        self.imagefile.write(content)
        self.imagefile.close()

        segments = self.proxy._get_file_segments(
            endpoint='test_container/test_image',
            filename=self.imagefile.name,
            file_size=file_size,
            segment_size=1000)
        self.assertEqual(len(segments), 5)
        segment_content = b''
        for (index, (name, segment)) in enumerate(segments.items()):
            self.assertEqual(
                'test_container/test_image/{index:0>6}'.format(index=index),
                name)
            segment_content += segment.read()
        self.assertEqual(content, segment_content)


class TestDownloadObject(base_test_object.BaseTestObject):

    def setUp(self):
        super(TestDownloadObject, self).setUp()
        self.the_data = b'test body'
        self.register_uris([
            dict(method='GET', uri=self.object_endpoint,
                 headers={
                     'Content-Length': str(len(self.the_data)),
                     'Content-Type': 'application/octet-stream',
                     'Accept-Ranges': 'bytes',
                     'Last-Modified': 'Thu, 15 Dec 2016 13:34:14 GMT',
                     'Etag': '"b5c454b44fbd5344793e3fb7e3850768"',
                     'X-Timestamp': '1481808853.65009',
                     'X-Trans-Id': 'tx68c2a2278f0c469bb6de1-005857ed80dfw1',
                     'Date': 'Mon, 19 Dec 2016 14:24:00 GMT',
                     'X-Static-Large-Object': 'True',
                     'X-Object-Meta-Mtime': '1481513709.168512',
                 },
                 content=self.the_data)])

    def test_download(self):
        data = self.cloud.object_store.download_object(
            self.object, container=self.container)

        self.assertEqual(data, self.the_data)
        self.assert_calls()

    def test_stream(self):
        chunk_size = 2
        for index, chunk in enumerate(self.cloud.object_store.stream_object(
                self.object, container=self.container,
                chunk_size=chunk_size)):
            chunk_len = len(chunk)
            start = index * chunk_size
            end = start + chunk_len
            self.assertLessEqual(chunk_len, chunk_size)
            self.assertEqual(chunk, self.the_data[start:end])
        self.assert_calls()


class TestExtractName(TestObjectStoreProxy):

    scenarios = [
        ('discovery', dict(url='/', parts=['account']))
    ]

    def test_extract_name(self):

        results = self.proxy._extract_name(self.url)
        self.assertEqual(self.parts, results)
