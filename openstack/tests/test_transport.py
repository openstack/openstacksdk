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
import logging

import fixtures
import httpretty
import mock
import requests
import six

from openstack import exceptions
from openstack.tests import base
from openstack import transport


fake_request = 'Now is the time...'
fake_response = 'for the quick brown fox...'
fake_response_json = '{"response": "for the quick brown fox..."}'
fake_redirect = 'redirect text'

fake_record1 = {
    'key1': {
        'id': '123',
        'name': 'OneTwoThree',
        'random': 'qwertyuiop',
    },
}

fake_record2 = {
    'hello': 'world',
}


class TestTransport(base.TestTransportBase):

    def setUp(self):
        super(TestTransport, self).setUp()

        self._orig_user_agent = transport.USER_AGENT
        self.test_user_agent = transport.USER_AGENT = "testing/1.0"

    def tearDown(self):
        super(TestTransport, self).tearDown()

        transport.USER_AGENT = self._orig_user_agent

    @httpretty.activate
    def test_request(self):
        self.stub_url(httpretty.GET, body=fake_response)
        xport = transport.Transport()
        resp = xport.request('GET', self.TEST_URL, accept=None)
        self.assertEqual(httpretty.GET, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_request_json(self):
        self.stub_url(httpretty.GET, json=fake_record1)
        xport = transport.Transport()
        resp = xport.request('GET', self.TEST_URL, accept=None)
        self.assertEqual(httpretty.GET, httpretty.last_request().method)
        self.assertResponseOK(resp, body=json.dumps(fake_record1))
        self.assertEqual(fake_record1, resp.json())

    @httpretty.activate
    def test_delete(self):
        self.stub_url(httpretty.DELETE, body=fake_response)
        xport = transport.Transport()
        resp = xport.delete(self.TEST_URL, accept=None)
        self.assertEqual(httpretty.DELETE, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_get(self):
        self.stub_url(httpretty.GET, body=fake_response)
        xport = transport.Transport()
        resp = xport.get(self.TEST_URL, accept=None)
        self.assertEqual(httpretty.GET, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_head(self):
        self.stub_url(httpretty.HEAD, body='')
        xport = transport.Transport()
        resp = xport.head(self.TEST_URL, accept=None)
        self.assertEqual(httpretty.HEAD, httpretty.last_request().method)
        self.assertResponseOK(resp, body='')

    @httpretty.activate
    def test_options(self):
        self.stub_url(httpretty.OPTIONS, body=fake_response)
        xport = transport.Transport()
        resp = xport.options(self.TEST_URL, accept=None)
        self.assertEqual(httpretty.OPTIONS, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_patch(self):
        self.stub_url(httpretty.PATCH, body=fake_response_json)
        xport = transport.Transport()
        resp = xport.patch(self.TEST_URL, json=fake_record2)
        self.assertEqual(httpretty.PATCH, httpretty.last_request().method)
        self.assertEqual(
            json.dumps(fake_record2),
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response_json)

    @httpretty.activate
    def test_post(self):
        self.stub_url(httpretty.POST, body=fake_response_json)
        xport = transport.Transport()
        resp = xport.post(self.TEST_URL, json=fake_record2)
        self.assertEqual(httpretty.POST, httpretty.last_request().method)
        self.assertEqual(
            json.dumps(fake_record2),
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response_json)

    @httpretty.activate
    def test_put(self):
        self.stub_url(httpretty.PUT, body=fake_response)
        xport = transport.Transport()

        resp = xport.put(self.TEST_URL, data=fake_request, accept=None)
        self.assertEqual(httpretty.PUT, httpretty.last_request().method)
        self.assertEqual(
            fake_request,
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_put_json(self):
        self.stub_url(httpretty.PUT, body=fake_response_json)
        xport = transport.Transport()

        resp = xport.put(self.TEST_URL, json=fake_record2)
        self.assertEqual(httpretty.PUT, httpretty.last_request().method)
        self.assertEqual(
            json.dumps(fake_record2),
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response_json)

    @httpretty.activate
    def test_request_accept(self):
        fake_record1_str = json.dumps(fake_record1)
        self.stub_url(httpretty.POST, body=fake_record1_str)
        xport = transport.Transport()
        resp = xport.post(self.TEST_URL, json=fake_record2, accept=None)
        self.assertRequestHeaderEqual('Accept', '*/*')
        self.assertEqual(fake_record1, resp.json())

        resp = xport.post(self.TEST_URL, json=fake_record2,
                          accept=transport.JSON)
        self.assertRequestHeaderEqual('Accept', transport.JSON)
        self.assertEqual(fake_record1, resp.json())

        xport = transport.Transport(accept=transport.JSON)
        resp = xport.post(self.TEST_URL, json=fake_record2)
        self.assertRequestHeaderEqual('Accept', transport.JSON)
        self.assertEqual(fake_record1, resp.json())

    @httpretty.activate
    def test_user_agent_no_arg(self):
        self.stub_url(httpretty.GET, body=fake_response)
        xport = transport.Transport()

        resp = xport.get(self.TEST_URL, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', self.test_user_agent)

        resp = xport.get(self.TEST_URL, headers={'User-Agent': None},
                         accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = xport.get(self.TEST_URL, user_agent=None, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', self.test_user_agent)

        resp = xport.get(self.TEST_URL, headers={'User-Agent': ''},
                         accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '')

        resp = xport.get(self.TEST_URL, user_agent='', accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', self.test_user_agent)

        new_agent = 'new-agent'
        resp = xport.get(self.TEST_URL, headers={'User-Agent': new_agent},
                         accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', new_agent)

        resp = xport.get(self.TEST_URL, user_agent=new_agent, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '%s %s' % (
                                      new_agent, self.test_user_agent))

        custom_value = 'new-agent'
        resp = xport.get(self.TEST_URL, headers={'User-Agent': custom_value},
                         user_agent=None, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', custom_value)

        override = 'overrides-agent'
        resp = xport.get(self.TEST_URL, headers={'User-Agent': None},
                         user_agent=override, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '%s %s' % (
                                      override, self.test_user_agent))

        resp = xport.get(self.TEST_URL, headers={'User-Agent': custom_value},
                         user_agent=override, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '%s %s' % (
                                      override, self.test_user_agent))

    @httpretty.activate
    def test_user_agent_arg_none(self):
        # None gets converted to the transport.USER_AGENT by default.
        self.stub_url(httpretty.GET, body=fake_response)
        xport = transport.Transport(user_agent=None)

        resp = xport.get(self.TEST_URL, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', self.test_user_agent)

    @httpretty.activate
    def test_user_agent_arg_default(self):
        self.stub_url(httpretty.GET, body=fake_response)
        agent = 'test-agent'
        xport = transport.Transport(user_agent=agent)

        resp = xport.get(self.TEST_URL, accept=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '%s %s' % (
                                      agent, self.test_user_agent))

    def test_verify_no_arg(self):
        xport = transport.Transport()
        self.assertTrue(xport.verify)

    def test_verify_arg_false(self):
        xport = transport.Transport(verify=False)
        self.assertFalse(xport.verify)

    def test_verify_arg_true(self):
        xport = transport.Transport(verify=True)
        self.assertTrue(xport.verify)

    def test_verify_arg_file(self):
        xport = transport.Transport(verify='ca-file')
        self.assertEqual('ca-file', xport.verify)

    @httpretty.activate
    def test_not_found(self):
        xport = transport.Transport()
        status = 404
        self.stub_url(httpretty.GET, status=status)

        exc = self.assertRaises(exceptions.HttpException, xport.get,
                                self.TEST_URL)
        self.assertEqual(status, exc.status_code)

    @httpretty.activate
    def test_server_error(self):
        xport = transport.Transport()
        status = 500
        self.stub_url(httpretty.GET, status=500)

        exc = self.assertRaises(exceptions.HttpException, xport.get,
                                self.TEST_URL)
        self.assertEqual(status, exc.status_code)


class TestTransportDebug(base.TestTransportBase):

    def setUp(self):
        super(TestTransportDebug, self).setUp()

        self.log_fixture = self.useFixture(
            fixtures.FakeLogger(level=logging.DEBUG),
        )

    @httpretty.activate
    def test_debug_post(self):
        self.stub_url(httpretty.POST, body=fake_response)
        xport = transport.Transport()
        headers = {
            'User-Agent': 'fake-curl',
            'X-Random-Header': 'x-random-value',
        }
        params = {
            'detailed-arg-name': 'qaz11 wsx22+edc33',
            'ssh_config_dir': '~/myusername/.ssh',
        }
        resp = xport.post(
            self.TEST_URL,
            headers=headers,
            params=params,
            json=fake_record2,
            accept=None,
        )
        self.assertEqual(httpretty.POST, httpretty.last_request().method)
        self.assertEqual(
            json.dumps(fake_record2),
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response)

        self.assertIn('curl', self.log_fixture.output)
        self.assertIn('POST', self.log_fixture.output)
        self.assertIn(
            'detailed-arg-name=qaz11+wsx22%2Bedc33',
            self.log_fixture.output,
        )
        self.assertIn(
            'ssh_config_dir=%7E%2Fmyusername%2F.ssh',
            self.log_fixture.output,
        )
        self.assertIn(json.dumps(fake_record2), self.log_fixture.output)
        self.assertIn(fake_response, self.log_fixture.output)

        for k, v in six.iteritems(headers):
            self.assertIn(k, self.log_fixture.output)
            self.assertIn(v, self.log_fixture.output)


class TestTransportRedirects(base.TestTransportBase):

    REDIRECT_CHAIN = [
        'http://myhost:3445/',
        'http://anotherhost:6555/',
        'http://thirdhost/',
        'http://finaldestination:55/',
    ]

    def setup_redirects(
            self,
            method=httpretty.GET,
            status=305,
            redirect_kwargs={},
            final_kwargs={},
    ):
        redirect_kwargs.setdefault('body', fake_redirect)

        for s, d in zip(self.REDIRECT_CHAIN, self.REDIRECT_CHAIN[1:]):
            httpretty.register_uri(
                method,
                s,
                status=status,
                location=d,
                **redirect_kwargs
            )

        final_kwargs.setdefault('status', 200)
        final_kwargs.setdefault('body', fake_response)
        httpretty.register_uri(method, self.REDIRECT_CHAIN[-1], **final_kwargs)

    @httpretty.activate
    def test_get_redirect(self):
        self.setup_redirects()
        xport = transport.Transport()
        resp = xport.get(self.REDIRECT_CHAIN[-2], accept=None)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_get_redirect_json(self):
        self.setup_redirects(
            final_kwargs={'body': fake_response_json},
        )
        xport = transport.Transport()
        resp = xport.get(self.REDIRECT_CHAIN[-2])
        self.assertResponseOK(resp, body=fake_response_json)

    @httpretty.activate
    def test_post_keeps_correct_method(self):
        self.setup_redirects(method=httpretty.POST, status=301)
        xport = transport.Transport()
        resp = xport.post(self.REDIRECT_CHAIN[-2], accept=None)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_post_keeps_correct_method_json(self):
        self.setup_redirects(
            method=httpretty.POST,
            status=301,
            final_kwargs={'body': fake_response_json},
        )
        xport = transport.Transport()
        resp = xport.post(self.REDIRECT_CHAIN[-2])
        self.assertResponseOK(resp, body=fake_response_json)

    @httpretty.activate
    def test_redirect_forever(self):
        self.setup_redirects()
        xport = transport.Transport()
        resp = xport.get(self.REDIRECT_CHAIN[0], accept=None)
        self.assertResponseOK(resp)
        # Request history length is 1 less than the source chain due to the
        # last response not being a redirect and not added to the history.
        self.assertEqual(len(self.REDIRECT_CHAIN) - 1, len(resp.history))

    @httpretty.activate
    def test_redirect_forever_json(self):
        self.setup_redirects(
            final_kwargs={'body': fake_response_json},
        )
        xport = transport.Transport()
        resp = xport.get(self.REDIRECT_CHAIN[0])
        self.assertResponseOK(resp)
        # Request history length is 1 less than the source chain due to the
        # last response not being a redirect and not added to the history.
        self.assertEqual(len(self.REDIRECT_CHAIN) - 1, len(resp.history))

    @httpretty.activate
    def test_no_redirect(self):
        self.setup_redirects()
        xport = transport.Transport(redirect=False)
        resp = xport.get(self.REDIRECT_CHAIN[0], accept=None)
        self.assertEqual(305, resp.status_code)
        self.assertEqual(self.REDIRECT_CHAIN[0], resp.url)

    @httpretty.activate
    def test_no_redirect_json(self):
        self.setup_redirects(
            final_kwargs={'body': fake_response_json},
        )
        xport = transport.Transport(redirect=False)
        self.assertRaises(
            exceptions.InvalidResponse,
            xport.get,
            self.REDIRECT_CHAIN[0],
        )

    @httpretty.activate
    def test_redirect_limit(self):
        self.setup_redirects()
        for i in (1, 2):
            xport = transport.Transport(redirect=i)
            resp = xport.get(self.REDIRECT_CHAIN[0], accept=None)
            self.assertResponseOK(resp, status=305, body=fake_redirect)
            self.assertEqual(self.REDIRECT_CHAIN[i], resp.url)

    @httpretty.activate
    def test_redirect_limit_json(self):
        self.setup_redirects(
            final_kwargs={'body': fake_response_json},
        )
        for i in (1, 2):
            xport = transport.Transport(redirect=i)
            self.assertRaises(
                exceptions.InvalidResponse,
                xport.get,
                self.REDIRECT_CHAIN[0],
            )

    @httpretty.activate
    def test_history_matches_requests(self):
        self.setup_redirects(status=301)
        xport = transport.Transport(redirect=True, accept=None)
        req_resp = requests.get(
            self.REDIRECT_CHAIN[0],
            allow_redirects=True,
        )

        resp = xport.get(self.REDIRECT_CHAIN[0])

        self.assertEqual(type(resp.history), type(req_resp.history))
        self.assertEqual(len(resp.history), len(req_resp.history))

        for r, s in zip(req_resp.history, resp.history):
            self.assertEqual(s.url, r.url)
            self.assertEqual(s.status_code, r.status_code)

    @httpretty.activate
    def test_history_matches_requests_json(self):
        self.setup_redirects(
            status=301,
            final_kwargs={'body': fake_response_json},
        )
        xport = transport.Transport(redirect=True)
        req_resp = requests.get(
            self.REDIRECT_CHAIN[0],
            allow_redirects=True,
        )

        resp = xport.get(self.REDIRECT_CHAIN[0])

        self.assertEqual(type(resp.history), type(req_resp.history))
        self.assertEqual(len(resp.history), len(req_resp.history))

        for r, s in zip(req_resp.history, resp.history):
            self.assertEqual(s.url, r.url)
            self.assertEqual(s.status_code, r.status_code)

    def test_parse_error_response(self):
        xport = transport.Transport(redirect=True)
        resp = mock.Mock()
        resp.json = mock.Mock()
        resp.json.return_value = {"badRequest": {"message": "Not defined"}}
        self.assertEqual("Not defined", xport._parse_error_response(resp))
        resp.json.return_value = {"message": {"response": "Not Allowed"}}
        self.assertEqual("Not Allowed", xport._parse_error_response(resp))
        resp.json.return_value = {"itemNotFound": {"message": "Not found"}}
        self.assertEqual("Not found", xport._parse_error_response(resp))
        resp.json.return_value = {"instanceFault": {"message": "Wot?"}}
        self.assertEqual("Wot?", xport._parse_error_response(resp))
        resp.json.return_value = {"QuantumError": "Network error"}
        self.assertEqual("Network error", xport._parse_error_response(resp))
