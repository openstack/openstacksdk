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
import warnings

from openstack import exceptions
from openstack import resource
from openstack.tests.unit import base
from openstack.tests.unit import fakes


class Test_Exception(base.TestCase):
    def test_method_not_supported(self):
        class FakeResource(resource.Resource):
            pass

        exc = exceptions.MethodNotSupported(FakeResource, 'list')
        expected = (
            'The list method is not supported for '
            'openstack.tests.unit.test_exceptions.FakeResource'
        )
        self.assertEqual(expected, str(exc))


class Test_HttpException(base.TestCase):
    def setUp(self):
        super().setUp()
        self.message = 'mayday'
        self.response = fakes.FakeResponse(
            status_code=401,
            data={
                'error': {
                    'code': 401,
                    'message': (
                        'The request you have made requires authentication.'
                    ),
                    'title': 'Unauthorized',
                },
            },
        )

    def _do_raise(self, *args, **kwargs):
        raise exceptions.HttpException(*args, **kwargs)

    def test_message(self):
        exc = self.assertRaises(
            exceptions.HttpException,
            self._do_raise,
            self.message,
            response=self.response,
        )

        self.assertEqual(self.message, exc.message)

    def test_details(self):
        details = "some details"
        exc = self.assertRaises(
            exceptions.HttpException,
            self._do_raise,
            self.message,
            response=self.response,
            details=details,
        )

        self.assertEqual(self.message, exc.message)
        self.assertEqual(details, exc.details)

    def test_http_status(self):
        http_status = 123
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            exc = self.assertRaises(
                exceptions.HttpException,
                self._do_raise,
                self.message,
                http_status=http_status,
            )

        self.assertEqual(self.message, exc.message)
        self.assertEqual(http_status, exc.status_code)

        self.assertIn(
            "The 'http_status' parameter is unnecessary",
            str(w[-1]),
        )


class TestRaiseFromResponse(base.TestCase):
    def setUp(self):
        super().setUp()
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
        exc = self.assertRaises(
            exceptions.NotFoundException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(self.message, exc.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(
            response.headers.get('x-openstack-request-id'), exc.request_id
        )

    def test_raise_bad_request_exception(self):
        response = mock.Mock()
        response.status_code = 400
        response.headers = {
            'content-type': 'application/json',
            'x-openstack-request-id': uuid.uuid4().hex,
        }
        exc = self.assertRaises(
            exceptions.BadRequestException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(self.message, exc.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(
            response.headers.get('x-openstack-request-id'), exc.request_id
        )

    def test_raise_http_exception(self):
        response = mock.Mock()
        response.status_code = 403
        response.headers = {
            'content-type': 'application/json',
            'x-openstack-request-id': uuid.uuid4().hex,
        }
        exc = self.assertRaises(
            exceptions.HttpException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(self.message, exc.message)
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(
            response.headers.get('x-openstack-request-id'), exc.request_id
        )

    def test_raise_compute_format(self):
        # Named faults: Nova, Cinder, Manila, Masakari, and Trove.
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
        exc = self.assertRaises(
            exceptions.NotFoundException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_network_format(self):
        # Neutron uses a fixed NeutronError envelope.
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
        exc = self.assertRaises(
            exceptions.NotFoundException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_placement_format(self):
        # Placement, Octavia, and Magnum use errors[*].detail.
        response = mock.Mock()
        response.status_code = 409
        response.headers = {'content-type': 'application/json'}
        response.json.return_value = {
            'errors': [
                {
                    'status': 409,
                    'title': 'Conflict',
                    'detail': self.message,
                }
            ]
        }
        exc = self.assertRaises(
            exceptions.ConflictException, self._do_raise, response
        )
        self.assertEqual(409, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_placement_error_details(self):
        # Robustness cases for errors[*].detail, not literal server responses.
        cases = [
            (
                [
                    {'detail': self.message},
                    {'detail': 'Another error\nwith more detail'},
                    {'title': 'No detail'},
                    {'detail': ''},
                    None,
                ],
                self.message + '\nAnother error\nwith more detail',
            ),
            ([], 'Conflict'),
            ([{}, {'detail': None}, None], 'Conflict'),
        ]
        for errors, expected in cases:
            with self.subTest(errors=errors):
                response = mock.Mock()
                response.status_code = 409
                response.reason = 'Conflict'
                response.headers = {'content-type': 'application/json'}
                response.json.return_value = {'errors': errors}
                exc = self.assertRaises(
                    exceptions.ConflictException, self._do_raise, response
                )
                self.assertEqual(expected, exc.details)

    def test_raise_json_encoded_fault_format(self):
        # Ironic, Cyborg, and Watcher wrap JSON text in error_message.
        response = mock.Mock()
        response.status_code = 404
        response.headers = {
            'content-type': 'application/json',
        }
        response.json.return_value = {
            'error_message': json.dumps(
                {
                    'faultstring': self.message,
                    'faultcode': 'Client',
                    'debuginfo': None,
                }
            )
        }
        exc = self.assertRaises(
            exceptions.NotFoundException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_object_wrapped_fault_format(self):
        # Aodh uses an object-valued error_message; also accept it for Ironic.
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
        exc = self.assertRaises(
            exceptions.NotFoundException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))

    def test_raise_root_error_formats(self):
        cases = [
            # Designate's ordinary errors have a root message.
            ({'message': self.message, 'code': 404}, self.message),
            # Glance also uses a root message, but code is a status string.
            (
                {
                    'message': self.message,
                    'code': '404 Not Found',
                    'title': 'Not Found',
                },
                self.message,
            ),
            # Mistral and Ironic's outer body-validation middleware.
            (
                {'faultstring': self.message, 'faultcode': 'Client'},
                self.message,
            ),
            # Synthetic root-list variants; no audited service requires these.
            ([{'message': self.message}], self.message),
            (
                [{'detail': self.message}, {'detail': 'Another error'}],
                self.message + '\nAnother error',
            ),
        ]
        for body, expected in cases:
            with self.subTest(body=body):
                response = fakes.FakeResponse(
                    status_code=404,
                    headers={'content-type': 'application/json'},
                    data=body,
                )
                exc = self.assertRaises(
                    exceptions.NotFoundException, self._do_raise, response
                )
                self.assertEqual(expected, exc.details)

    def test_raise_nested_error_formats(self):
        cases = [
            # Designate nests its validation-error collection in errors.
            {'errors': {'errors': [{'message': self.message}]}},
            # Synthetic combinations below exercise permissive traversal,
            # mixed entries, repeated encoding, and root-message precedence.
            {
                'error_message': json.dumps(
                    {'error': {'message': self.message}}
                )
            },
            {'errors': [None, 404, {}, {'detail': self.message}, 'metadata']},
            json.dumps(json.dumps({'faultstring': self.message})),
            {
                'message': self.message,
                'metadata': {'message': 'Not the principal error'},
            },
        ]
        for body in cases:
            with self.subTest(body=body):
                response = fakes.FakeResponse(
                    status_code=404,
                    headers={'content-type': 'application/json'},
                    data=body,
                )
                exc = self.assertRaises(
                    exceptions.NotFoundException, self._do_raise, response
                )
                self.assertEqual(self.message, exc.details)

    def test_raise_description_formats(self):
        cases = [
            # Barbican uses code/title/description.
            {
                'code': 400,
                'title': 'Bad Request',
                'description': self.message,
            },
            # Zaqar uses title/description; Gnocchi can use a text description.
            {'title': 'Invalid API request', 'description': self.message},
            # Keystone OAuth2 uses a string error code and error_description.
            {'error': 'invalid_request', 'error_description': self.message},
            # Heat may omit error.message for an unsafe exception.
            {
                'code': 400,
                'explanation': self.message,
                'error': {'type': 'Exception', 'traceback': None},
            },
            # Magnum preserves WebOb fields for some microversion errors.
            {
                'errors': [
                    {
                        'title': 'Requested microversion is unsupported',
                        'explanation': self.message,
                        'min_version': '1.1',
                        'max_version': '1.14',
                    }
                ]
            },
            # Ironic, Cyborg, Watcher, and Aodh can wrap non-JSON text.
            {'error_message': self.message},
        ]
        for body in cases:
            with self.subTest(body=body):
                response = fakes.FakeResponse(
                    status_code=400,
                    headers={'content-type': 'application/json'},
                    data=body,
                )
                exc = self.assertRaises(
                    exceptions.BadRequestException, self._do_raise, response
                )
                self.assertEqual(self.message, exc.details)

    def test_extract_messages_prefers_structured_errors(self):
        # Synthetic combinations ensure fallback text does not mask a more
        # specific message or return an encoded fault verbatim.
        cases = [
            {
                'description': 'Generic description',
                'message': self.message,
            },
            {
                'explanation': 'Generic explanation',
                'error': {'message': self.message},
            },
            {
                'description': 'Generic description',
                'errors': [{'detail': self.message}],
            },
            {
                'error_message': json.dumps({'faultstring': self.message}),
            },
            {
                'error_message': {'faultstring': self.message},
            },
        ]
        for body in cases:
            with self.subTest(body=body):
                self.assertEqual(
                    self.message, exceptions._extract_messages(body)
                )

    def test_extract_messages_ignores_non_errors(self):
        # Synthetic inputs ensure metadata/scalars are not treated as errors.
        cases: list[object] = [
            None,
            True,
            404,
            '404',
            'null',
            'true',
            'metadata',
            json.dumps('metadata'),
            [],
            {},
            {'code': 404, 'title': 'Not Found'},
            {'errors': [None, {}, {'detail': ''}]},
            {
                'description': '',
                'error_description': None,
                'explanation': '',
                'error_message': None,
            },
            {
                'title': 'Not Found',
                'request_id': 'request-id',
                'traceback': 'Private debug information',
            },
        ]
        for body in cases:
            with self.subTest(body=body):
                self.assertIsNone(exceptions._extract_messages(body))

    def test_raise_wsme_format(self):
        # Mistral exposes WSME faults without an error_message wrapper.
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
        exc = self.assertRaises(
            exceptions.NotFoundException,
            self._do_raise,
            response,
            error_message=self.message,
        )
        self.assertEqual(response.status_code, exc.status_code)
        self.assertEqual(self.message, exc.details)
        self.assertIn(self.message, str(exc))
