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

import mock
import testtools

from keystoneauth1 import exceptions as _exceptions

from openstack import exceptions
from openstack.image import image_service
from openstack import session


class TestSession(testtools.TestCase):

    def test_parse_url(self):
        filt = image_service.ImageService()
        self.assertEqual(
            "http://127.0.0.1:9292/v1",
            session.parse_url(filt, "http://127.0.0.1:9292"))
        self.assertEqual(
            "http://127.0.0.1:9292/foo/v1",
            session.parse_url(filt, "http://127.0.0.1:9292/foo"))
        self.assertEqual(
            "http://127.0.0.1:9292/v2",
            session.parse_url(filt, "http://127.0.0.1:9292/v2.0"))
        filt.version = 'v1'
        self.assertEqual(
            "http://127.0.0.1:9292/v1/mytenant",
            session.parse_url(filt, "http://127.0.0.1:9292/v2.0/mytenant/"))
        self.assertEqual(
            "http://127.0.0.1:9292/wot/v1/mytenant",
            session.parse_url(filt, "http://127.0.0.1:9292/wot/v2.0/mytenant"))

    def test_user_agent_none(self):
        sot = session.Session(None)
        self.assertTrue(sot.user_agent.startswith("openstacksdk"))

    def test_user_agent_set(self):
        sot = session.Session(None, user_agent="testing/123")
        self.assertTrue(sot.user_agent.startswith("testing/123 openstacksdk"))

    def test_map_exceptions_not_found_exception(self):
        ksa_exc = _exceptions.HttpError(message="test", http_status=404)
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.NotFoundException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.NotFoundException)
        self.assertEqual(ksa_exc.message, os_exc.message)
        self.assertEqual(ksa_exc.http_status, os_exc.http_status)
        self.assertEqual(ksa_exc, os_exc.cause)

    def test_map_exceptions_http_exception(self):
        ksa_exc = _exceptions.HttpError(message="test", http_status=400)
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.HttpException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.HttpException)
        self.assertEqual(ksa_exc.message, os_exc.message)
        self.assertEqual(ksa_exc.http_status, os_exc.http_status)
        self.assertEqual(ksa_exc, os_exc.cause)

    def test_map_exceptions_sdk_exception_1(self):
        ksa_exc = _exceptions.ClientException()
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.SDKException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.SDKException)
        self.assertEqual(ksa_exc, os_exc.cause)

    def test_map_exceptions_sdk_exception_2(self):
        ksa_exc = _exceptions.VersionNotAvailable()
        func = mock.Mock(side_effect=ksa_exc)

        os_exc = self.assertRaises(
            exceptions.SDKException, session.map_exceptions(func))
        self.assertIsInstance(os_exc, exceptions.SDKException)
        self.assertEqual(ksa_exc, os_exc.cause)
