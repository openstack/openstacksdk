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

from hashlib import sha1
import random
import string
import tempfile
import time
from unittest import mock

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
        content = ''.join(random.choice(
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
        ('discovery', dict(url='/', parts=['account'])),
        ('endpoints', dict(url='/endpoints', parts=['endpoints'])),
        ('container', dict(url='/AUTH_123/container_name',
                           parts=['container'])),
        ('object', dict(url='/container_name/object_name',
                        parts=['object'])),
        ('object_long', dict(url='/v1/AUTH_123/cnt/path/deep/object_name',
                             parts=['object']))
    ]

    def test_extract_name(self):

        results = self.proxy._extract_name(self.url, project_id='123')
        self.assertEqual(self.parts, results)


class TestTempURL(TestObjectStoreProxy):
    expires_iso8601_format = '%Y-%m-%dT%H:%M:%SZ'
    short_expires_iso8601_format = '%Y-%m-%d'
    time_errmsg = ('time must either be a whole number or in specific '
                   'ISO 8601 format.')
    path_errmsg = 'path must be full path to an object e.g. /v1/a/c/o'
    url = '/v1/AUTH_account/c/o'
    seconds = 3600
    key = 'correcthorsebatterystaple'
    method = 'GET'
    expected_url = url + ('?temp_url_sig=temp_url_signature'
                          '&temp_url_expires=1400003600')
    expected_body = '\n'.join([
        method,
        '1400003600',
        url,
    ]).encode('utf-8')

    @mock.patch('hmac.HMAC')
    @mock.patch('time.time', return_value=1400000000)
    def test_generate_temp_url(self, time_mock, hmac_mock):
        hmac_mock().hexdigest.return_value = 'temp_url_signature'
        url = self.proxy.generate_temp_url(
            self.url, self.seconds, self.method, temp_url_key=self.key)
        key = self.key
        if not isinstance(key, bytes):
            key = key.encode('utf-8')
        self.assertEqual(url, self.expected_url)
        self.assertEqual(hmac_mock.mock_calls, [
            mock.call(),
            mock.call(key, self.expected_body, sha1),
            mock.call().hexdigest(),
        ])
        self.assertIsInstance(url, type(self.url))

    @mock.patch('hmac.HMAC')
    @mock.patch('time.time', return_value=1400000000)
    def test_generate_temp_url_ip_range(self, time_mock, hmac_mock):
        hmac_mock().hexdigest.return_value = 'temp_url_signature'
        ip_ranges = [
            '1.2.3.4', '1.2.3.4/24', '2001:db8::',
            b'1.2.3.4', b'1.2.3.4/24', b'2001:db8::',
        ]
        path = '/v1/AUTH_account/c/o/'
        expected_url = path + ('?temp_url_sig=temp_url_signature'
                               '&temp_url_expires=1400003600'
                               '&temp_url_ip_range=')
        for ip_range in ip_ranges:
            hmac_mock.reset_mock()
            url = self.proxy.generate_temp_url(
                path, self.seconds, self.method,
                temp_url_key=self.key, ip_range=ip_range)
            key = self.key
            if not isinstance(key, bytes):
                key = key.encode('utf-8')

            if isinstance(ip_range, bytes):
                ip_range_expected_url = (
                    expected_url + ip_range.decode('utf-8')
                )
                expected_body = '\n'.join([
                    'ip=' + ip_range.decode('utf-8'),
                    self.method,
                    '1400003600',
                    path,
                ]).encode('utf-8')
            else:
                ip_range_expected_url = expected_url + ip_range
                expected_body = '\n'.join([
                    'ip=' + ip_range,
                    self.method,
                    '1400003600',
                    path,
                ]).encode('utf-8')

            self.assertEqual(url, ip_range_expected_url)

            self.assertEqual(hmac_mock.mock_calls, [
                mock.call(key, expected_body, sha1),
                mock.call().hexdigest(),
            ])
            self.assertIsInstance(url, type(path))

    @mock.patch('hmac.HMAC')
    def test_generate_temp_url_iso8601_argument(self, hmac_mock):
        hmac_mock().hexdigest.return_value = 'temp_url_signature'
        url = self.proxy.generate_temp_url(
            self.url, '2014-05-13T17:53:20Z', self.method,
            temp_url_key=self.key)
        self.assertEqual(url, self.expected_url)

        # Don't care about absolute arg.
        url = self.proxy.generate_temp_url(self.url, '2014-05-13T17:53:20Z',
                                           self.method,
                                           temp_url_key=self.key,
                                           absolute=True)
        self.assertEqual(url, self.expected_url)

        lt = time.localtime()
        expires = time.strftime(self.expires_iso8601_format[:-1], lt)

        if not isinstance(self.expected_url, str):
            expected_url = self.expected_url.replace(
                b'1400003600', bytes(str(int(time.mktime(lt))),
                                     encoding='ascii'))
        else:
            expected_url = self.expected_url.replace(
                '1400003600', str(int(time.mktime(lt))))
        url = self.proxy.generate_temp_url(self.url, expires,
                                           self.method,
                                           temp_url_key=self.key)
        self.assertEqual(url, expected_url)

        expires = time.strftime(self.short_expires_iso8601_format, lt)
        lt = time.strptime(expires, self.short_expires_iso8601_format)

        if not isinstance(self.expected_url, str):
            expected_url = self.expected_url.replace(
                b'1400003600', bytes(str(int(time.mktime(lt))),
                                     encoding='ascii'))
        else:
            expected_url = self.expected_url.replace(
                '1400003600', str(int(time.mktime(lt))))
        url = self.proxy.generate_temp_url(self.url, expires,
                                           self.method,
                                           temp_url_key=self.key)
        self.assertEqual(url, expected_url)

    @mock.patch('hmac.HMAC')
    @mock.patch('time.time', return_value=1400000000)
    def test_generate_temp_url_iso8601_output(self, time_mock, hmac_mock):
        hmac_mock().hexdigest.return_value = 'temp_url_signature'
        url = self.proxy.generate_temp_url(self.url, self.seconds,
                                           self.method,
                                           temp_url_key=self.key,
                                           iso8601=True)
        key = self.key
        if not isinstance(key, bytes):
            key = key.encode('utf-8')

        expires = time.strftime(self.expires_iso8601_format,
                                time.gmtime(1400003600))
        if not isinstance(self.url, str):
            self.assertTrue(url.endswith(bytes(expires, 'utf-8')))
        else:
            self.assertTrue(url.endswith(expires))
        self.assertEqual(hmac_mock.mock_calls, [
            mock.call(),
            mock.call(key, self.expected_body, sha1),
            mock.call().hexdigest(),
        ])
        self.assertIsInstance(url, type(self.url))

    @mock.patch('hmac.HMAC')
    @mock.patch('time.time', return_value=1400000000)
    def test_generate_temp_url_prefix(self, time_mock, hmac_mock):
        hmac_mock().hexdigest.return_value = 'temp_url_signature'
        prefixes = ['', 'o', 'p0/p1/']
        for p in prefixes:
            hmac_mock.reset_mock()
            path = '/v1/AUTH_account/c/' + p
            expected_url = path + ('?temp_url_sig=temp_url_signature'
                                   '&temp_url_expires=1400003600'
                                   '&temp_url_prefix=' + p)
            expected_body = '\n'.join([
                self.method,
                '1400003600',
                'prefix:' + path,
            ]).encode('utf-8')
            url = self.proxy.generate_temp_url(
                path, self.seconds, self.method, prefix=True,
                temp_url_key=self.key)
            key = self.key
            if not isinstance(key, bytes):
                key = key.encode('utf-8')
            self.assertEqual(url, expected_url)
            self.assertEqual(hmac_mock.mock_calls, [
                mock.call(key, expected_body, sha1),
                mock.call().hexdigest(),
            ])

            self.assertIsInstance(url, type(path))

    def test_generate_temp_url_invalid_path(self):
        self.assertRaisesRegex(
            ValueError,
            'path must be representable as UTF-8',
            self.proxy.generate_temp_url, b'/v1/a/c/\xff', self.seconds,
            self.method, temp_url_key=self.key)

    @mock.patch('hmac.HMAC.hexdigest', return_value="temp_url_signature")
    def test_generate_absolute_expiry_temp_url(self, hmac_mock):
        if isinstance(self.expected_url, bytes):
            expected_url = self.expected_url.replace(
                b'1400003600', b'2146636800')
        else:
            expected_url = self.expected_url.replace(
                u'1400003600', u'2146636800')
        url = self.proxy.generate_temp_url(
            self.url, 2146636800, self.method, absolute=True,
            temp_url_key=self.key)
        self.assertEqual(url, expected_url)

    def test_generate_temp_url_bad_time(self):
        for bad_time in ['not_an_int', -1, 1.1, '-1', '1.1', '2015-05',
                         '2015-05-01T01:00']:
            self.assertRaisesRegex(
                ValueError, self.time_errmsg,
                self.proxy.generate_temp_url, self.url, bad_time,
                self.method, temp_url_key=self.key)

    def test_generate_temp_url_bad_path(self):
        for bad_path in ['/v1/a/c', 'v1/a/c/o', 'blah/v1/a/c/o', '/v1//c/o',
                         '/v1/a/c/', '/v1/a/c']:
            self.assertRaisesRegex(
                ValueError, self.path_errmsg,
                self.proxy.generate_temp_url, bad_path, 60, self.method,
                temp_url_key=self.key)


class TestTempURLUnicodePathAndKey(TestTempURL):
    url = u'/v1/\u00e4/c/\u00f3'
    key = u'k\u00e9y'
    expected_url = (u'%s?temp_url_sig=temp_url_signature'
                    u'&temp_url_expires=1400003600') % url
    expected_body = u'\n'.join([
        u'GET',
        u'1400003600',
        url,
    ]).encode('utf-8')


class TestTempURLUnicodePathBytesKey(TestTempURL):
    url = u'/v1/\u00e4/c/\u00f3'
    key = u'k\u00e9y'.encode('utf-8')
    expected_url = (u'%s?temp_url_sig=temp_url_signature'
                    u'&temp_url_expires=1400003600') % url
    expected_body = '\n'.join([
        u'GET',
        u'1400003600',
        url,
    ]).encode('utf-8')


class TestTempURLBytesPathUnicodeKey(TestTempURL):
    url = u'/v1/\u00e4/c/\u00f3'.encode('utf-8')
    key = u'k\u00e9y'
    expected_url = url + (b'?temp_url_sig=temp_url_signature'
                          b'&temp_url_expires=1400003600')
    expected_body = b'\n'.join([
        b'GET',
        b'1400003600',
        url,
    ])


class TestTempURLBytesPathAndKey(TestTempURL):
    url = u'/v1/\u00e4/c/\u00f3'.encode('utf-8')
    key = u'k\u00e9y'.encode('utf-8')
    expected_url = url + (b'?temp_url_sig=temp_url_signature'
                          b'&temp_url_expires=1400003600')
    expected_body = b'\n'.join([
        b'GET',
        b'1400003600',
        url,
    ])


class TestTempURLBytesPathAndNonUtf8Key(TestTempURL):
    url = u'/v1/\u00e4/c/\u00f3'.encode('utf-8')
    key = b'k\xffy'
    expected_url = url + (b'?temp_url_sig=temp_url_signature'
                          b'&temp_url_expires=1400003600')
    expected_body = b'\n'.join([
        b'GET',
        b'1400003600',
        url,
    ])
