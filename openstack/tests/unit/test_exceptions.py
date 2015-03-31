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

    def test_status_code(self):
        status_code = 123
        exc = self.assertRaises(exceptions.HttpException,
                                self._do_raise, self.message,
                                status_code=status_code)

        self.assertEqual(self.message, exc.message)
        self.assertEqual(status_code, exc.status_code)
