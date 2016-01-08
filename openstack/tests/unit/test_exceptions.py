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

import testtools

from openstack import exceptions


class Test_Exception(testtools.TestCase):
    def test_method_not_supported(self):
        exc = exceptions.MethodNotSupported(self.__class__, 'list')
        expected = ('The list method is not supported for ' +
                    'openstack.tests.unit.test_exceptions.Test_Exception')
        self.assertEqual(expected, str(exc))


class Test_HttpException(testtools.TestCase):

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
        self.assertEqual(http_status, exc.http_status)
