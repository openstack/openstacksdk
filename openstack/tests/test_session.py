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

from openstack.auth import service_filter
from openstack import session
from openstack.tests import base
from openstack.tests import fakes


class TestSession(base.TestCase):

    TEST_PATH = '/test/path'

    def setUp(self):
        super(TestSession, self).setUp()
        self.xport = fakes.FakeTransport()
        self.auth = fakes.FakeAuthenticator()
        self.serv = service_filter.ServiceFilter(service_type='identity')
        self.sess = session.Session(self.xport, self.auth)
        self.expected = {'headers': {'X-Auth-Token': self.auth.TOKEN}}

    def test_head(self):
        resp = self.sess.head(self.TEST_PATH, service=self.serv)

        self.assertEqual(self.xport.RESPONSE, resp)
        self.auth.get_token.assert_called_with(self.xport)
        self.auth.get_endpoint.assert_called_with(self.xport, self.serv)
        url = self.auth.ENDPOINT + self.TEST_PATH
        self.xport.request.assert_called_with('HEAD', url, **self.expected)

    def test_get(self):
        resp = self.sess.get(self.TEST_PATH, service=self.serv)

        self.assertEqual(self.xport.RESPONSE, resp)
        self.auth.get_token.assert_called_with(self.xport)
        self.auth.get_endpoint.assert_called_with(self.xport, self.serv)
        url = self.auth.ENDPOINT + self.TEST_PATH
        self.xport.request.assert_called_with('GET', url, **self.expected)

    def test_post(self):
        resp = self.sess.post(self.TEST_PATH, service=self.serv)

        self.assertEqual(self.xport.RESPONSE, resp)
        self.auth.get_token.assert_called_with(self.xport)
        self.auth.get_endpoint.assert_called_with(self.xport, self.serv)
        url = self.auth.ENDPOINT + self.TEST_PATH
        self.xport.request.assert_called_with('POST', url, **self.expected)

    def test_put(self):
        resp = self.sess.put(self.TEST_PATH, service=self.serv)

        self.assertEqual(self.xport.RESPONSE, resp)
        self.auth.get_token.assert_called_with(self.xport)
        self.auth.get_endpoint.assert_called_with(self.xport, self.serv)
        url = self.auth.ENDPOINT + self.TEST_PATH
        self.xport.request.assert_called_with('PUT', url, **self.expected)

    def test_delete(self):
        resp = self.sess.delete(self.TEST_PATH, service=self.serv)

        self.assertEqual(self.xport.RESPONSE, resp)
        self.auth.get_token.assert_called_with(self.xport)
        self.auth.get_endpoint.assert_called_with(self.xport, self.serv)
        url = self.auth.ENDPOINT + self.TEST_PATH
        self.xport.request.assert_called_with('DELETE', url, **self.expected)

    def test_patch(self):
        resp = self.sess.patch(self.TEST_PATH, service=self.serv)

        self.assertEqual(self.xport.RESPONSE, resp)
        self.auth.get_token.assert_called_with(self.xport)
        self.auth.get_endpoint.assert_called_with(self.xport, self.serv)
        url = self.auth.ENDPOINT + self.TEST_PATH
        self.xport.request.assert_called_with('PATCH', url, **self.expected)
