# -*- coding: utf-8 -*-

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
from unittest import mock
import uuid

from openstack import exceptions
from openstack.tests.unit import base


class Test_Exception(base.TestCase):
    def test_method_not_supported(self):
        exc = exceptions.MethodNotSupported(self.__class__, 'list')
        expected = ('The list method is not supported for '
                    + 'openstack.tests.unit.test_exceptions.Test_Exception')
        self.assertEqual(expected, str(exc))


class Test_HttpException(base.TestCase):

    def setUp(self):
        super(Test_HttpException, self).setUp()
        self.message = "mayday"

    def _do_raise(self, *args, **kwargs):
        raise exceptions.HttpException(*args, **kwargs)

    def test_message(self):
        exc = self.assertRaises(exceptions.HttpException,
                                self._do_raise, self.message)

        self.assertEqual(self.message, exc.message)

    def test_details(self):
        details = "some details"
        exc = self.assertRaises(exceptions.HttpException,
                                self._do_raise, self.message,
                                details=details)

        self.assertEqual(self.message, exc.message)
        self.assertEqual(details, exc.details)

    def test_http_status(self):
        http_status = 123
        exc = self.assertRaises(exceptions.HttpException,
                                self._do_raise, self.message,
                                http_status=http_status)

        self.assertEqual(self.message, exc.message)
        self.assertEqual(http_status, exc.status_code)

    def test_unicode_message(self):
        unicode_message = u"Event: No item found for does_not_exist©"
        http_exception = exceptions.HttpException(message=unicode_message)
        try:
            http_exception.__unicode__()
        except Exception:
            self.fail("HttpException unicode message error")


class TestRaiseFromResponse(base.TestCase):

    def setUp(self):
        super(TestRaiseFromResponse, self).setUp()
        self.message = "Where is my kitty?"

    def _do_raise(self, *args, **kwargs):
        return exceptions.raise_from_response(*args, **kwargs)

    def test_raise_no_exception(self):
        response = mock.Mock()
        response.status_code = 200
        self.assertIsNone(self._do_raise(response))

    def test_raise_not_found_exception(self):
        response = mock.Mock()
        response.status_code = 404
        response.headers = {
            'content-type': 'application/json',
            'x-openstack-request-id': uuid.uuid4().hex,
        }
        exc = self.assertRaises(exceptions.NotFoundException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(self.message, exc.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(
            response.headers.get('x-openstack-request-id'),
            exc.request_id
        )

    def test_raise_bad_request_exception(self):
        response = mock.Mock()
        response.status_code = 400
        response.headers = {
            'content-type': 'application/json',
            'x-openstack-request-id': uuid.uuid4().hex,
        }
        exc = self.assertRaises(exceptions.BadRequestException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(self.message, exc.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(
            response.headers.get('x-openstack-request-id'),
            exc.request_id
        )

    def test_raise_http_exception(self):
        response = mock.Mock()
        response.status_code = 403
        response.headers = {
            'content-type': 'application/json',
            'x-openstack-request-id': uuid.uuid4().hex,
        }
        exc = self.assertRaises(exceptions.HttpException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(self.message, exc.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(
            response.headers.get('x-openstack-request-id'),
            exc.request_id
        )

    def test_raise_compute_format(self):
        response = mock.Mock()
        response.status_code = 404
        response.headers = {
            'content-type': 'application/json',
        }
        response.json.return_value = {
            'itemNotFound': {
                'message': self.message,
                'code': 404,
            }
        }
        exc = self.assertRaises(exceptions.NotFoundException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_network_format(self):
        response = mock.Mock()
        response.status_code = 404
        response.headers = {
            'content-type': 'application/json',
        }
        response.json.return_value = {
            'NeutronError': {
                'message': self.message,
                'type': 'FooNotFound',
                'detail': '',
            }
        }
        exc = self.assertRaises(exceptions.NotFoundException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_baremetal_old_format(self):
        response = mock.Mock()
        response.status_code = 404
        response.headers = {
            'content-type': 'application/json',
        }
        response.json.return_value = {
            'error_message': json.dumps({
                'faultstring': self.message,
                'faultcode': 'Client',
                'debuginfo': None,
            })
        }
        exc = self.assertRaises(exceptions.NotFoundException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_baremetal_corrected_format(self):
        response = mock.Mock()
        response.status_code = 404
        response.headers = {
            'content-type': 'application/json',
        }
        response.json.return_value = {
            'error_message': {
                'faultstring': self.message,
                'faultcode': 'Client',
                'debuginfo': None,
            }
        }
        exc = self.assertRaises(exceptions.NotFoundException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_wsme_format(self):
        response = mock.Mock()
        response.status_code = 404
        response.headers = {
            'content-type': 'application/json',
        }
        response.json.return_value = {
            'faultstring': self.message,
            'faultcode': 'Client',
            'debuginfo': None,
        }
        exc = self.assertRaises(exceptions.NotFoundException,
                                self._do_raise, response,
                                error_message=self.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))
