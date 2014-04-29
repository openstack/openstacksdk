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
import six

import fixtures
import httpretty

import requests

from openstack.tests import base
from openstack import transport


fake_request = 'Now is the time...'
fake_response = 'for the quick brown fox...'
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

    @httpretty.activate
    def test_request(self):
        self.stub_url(httpretty.GET, body=fake_response)
        sess = transport.Transport()
        resp = sess.request('GET', self.TEST_URL)
        self.assertEqual(httpretty.GET, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_request_json(self):
        self.stub_url(httpretty.GET, json=fake_record1)
        sess = transport.Transport()
        resp = sess.request('GET', self.TEST_URL)
        self.assertEqual(httpretty.GET, httpretty.last_request().method)
        self.assertResponseOK(resp, body=json.dumps(fake_record1))
        self.assertEqual(fake_record1, resp.json())

    @httpretty.activate
    def test_delete(self):
        self.stub_url(httpretty.DELETE, body=fake_response)
        sess = transport.Transport()
        resp = sess.delete(self.TEST_URL)
        self.assertEqual(httpretty.DELETE, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_get(self):
        self.stub_url(httpretty.GET, body=fake_response)
        sess = transport.Transport()
        resp = sess.get(self.TEST_URL)
        self.assertEqual(httpretty.GET, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_head(self):
        self.stub_url(httpretty.HEAD, body=fake_response)
        sess = transport.Transport()
        resp = sess.head(self.TEST_URL)
        self.assertEqual(httpretty.HEAD, httpretty.last_request().method)
        self.assertResponseOK(resp, body='')

    @httpretty.activate
    def test_options(self):
        self.stub_url(httpretty.OPTIONS, body=fake_response)
        sess = transport.Transport()
        resp = sess.options(self.TEST_URL)
        self.assertEqual(httpretty.OPTIONS, httpretty.last_request().method)
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_patch(self):
        self.stub_url(httpretty.PATCH, body=fake_response)
        sess = transport.Transport()
        resp = sess.patch(self.TEST_URL, json=fake_record2)
        self.assertEqual(httpretty.PATCH, httpretty.last_request().method)
        self.assertEqual(
            json.dumps(fake_record2),
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_post(self):
        self.stub_url(httpretty.POST, body=fake_response)
        sess = transport.Transport()
        resp = sess.post(self.TEST_URL, json=fake_record2)
        self.assertEqual(httpretty.POST, httpretty.last_request().method)
        self.assertEqual(
            json.dumps(fake_record2),
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_put(self):
        self.stub_url(httpretty.PUT, body=fake_response)
        sess = transport.Transport()

        resp = sess.put(self.TEST_URL, data=fake_request)
        self.assertEqual(httpretty.PUT, httpretty.last_request().method)
        self.assertEqual(
            fake_request,
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response)

        resp = sess.put(self.TEST_URL, json=fake_record2)
        self.assertEqual(httpretty.PUT, httpretty.last_request().method)
        self.assertEqual(
            json.dumps(fake_record2),
            httpretty.last_request().body.decode('utf-8'),
        )
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_user_agent_no_arg(self):
        self.stub_url(httpretty.GET, body=fake_response)
        sess = transport.Transport()

        resp = sess.get(self.TEST_URL)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual(
            'User-Agent',
            transport.DEFAULT_USER_AGENT,
        )

        resp = sess.get(self.TEST_URL, headers={'User-Agent': None})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(self.TEST_URL, user_agent=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(self.TEST_URL, headers={'User-Agent': ''})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '')

        resp = sess.get(self.TEST_URL, user_agent='')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '')

        resp = sess.get(self.TEST_URL, headers={'User-Agent': 'new-agent'})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = sess.get(self.TEST_URL, user_agent='new-agent')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': 'new-agent'},
            user_agent=None,
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': None},
            user_agent='overrides-agent',
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': 'new-agent'},
            user_agent='overrides-agent',
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

    @httpretty.activate
    def test_user_agent_arg_none(self):
        self.stub_url(httpretty.GET, body=fake_response)
        sess = transport.Transport(user_agent=None)

        resp = sess.get(self.TEST_URL)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual(
            'User-Agent',
            transport.DEFAULT_USER_AGENT,
        )

        resp = sess.get(self.TEST_URL, headers={'User-Agent': None})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(self.TEST_URL, user_agent=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(self.TEST_URL, headers={'User-Agent': ''})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '')

        resp = sess.get(self.TEST_URL, user_agent='')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '')

        resp = sess.get(self.TEST_URL, headers={'User-Agent': 'new-agent'})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = sess.get(self.TEST_URL, user_agent='new-agent')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': 'new-agent'},
            user_agent=None,
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': None},
            user_agent='overrides-agent',
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': 'new-agent'},
            user_agent='overrides-agent',
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

    @httpretty.activate
    def test_user_agent_arg_default(self):
        self.stub_url(httpretty.GET, body=fake_response)
        sess = transport.Transport(user_agent='test-agent')

        resp = sess.get(self.TEST_URL)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'test-agent')

        resp = sess.get(self.TEST_URL, headers={'User-Agent': None})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(self.TEST_URL, user_agent=None)
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(self.TEST_URL, headers={'User-Agent': ''})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '')

        resp = sess.get(self.TEST_URL, user_agent='')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', '')

        resp = sess.get(self.TEST_URL, headers={'User-Agent': 'new-agent'})
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = sess.get(self.TEST_URL, user_agent='new-agent')
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'new-agent')

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': 'new-agent'},
            user_agent=None,
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', None)

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': None},
            user_agent='overrides-agent',
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

        resp = sess.get(
            self.TEST_URL,
            headers={'User-Agent': 'new-agent'},
            user_agent='overrides-agent',
        )
        self.assertTrue(resp.ok)
        self.assertRequestHeaderEqual('User-Agent', 'overrides-agent')

    def test_verify_no_arg(self):
        sess = transport.Transport()
        self.assertTrue(sess.verify)

    def test_verify_arg_none(self):
        sess = transport.Transport(verify=None)
        self.assertIsNone(sess.verify)

    def test_verify_arg_false(self):
        sess = transport.Transport(verify=False)
        self.assertFalse(sess.verify)

    def test_verify_arg_true(self):
        sess = transport.Transport(verify=True)
        self.assertTrue(sess.verify)

    def test_verify_arg_file(self):
        sess = transport.Transport(verify='ca-file')
        self.assertEqual('ca-file', sess.verify)

    @httpretty.activate
    def test_not_found(self):
        sess = transport.Transport()
        self.stub_url(httpretty.GET, status=404)

        resp = sess.get(self.TEST_URL)
        self.assertFalse(resp.ok)
        self.assertEqual(404, resp.status_code)

    @httpretty.activate
    def test_server_error(self):
        sess = transport.Transport()
        self.stub_url(httpretty.GET, status=500)

        resp = sess.get(self.TEST_URL)
        self.assertFalse(resp.ok)
        self.assertEqual(500, resp.status_code)


class TestTransportDebug(base.TestTransportBase):

    def setUp(self):
        super(TestTransportDebug, self).setUp()

        self.log_fixture = self.useFixture(
            fixtures.FakeLogger(level=logging.DEBUG),
        )

    @httpretty.activate
    def test_debug_post(self):
        self.stub_url(httpretty.POST, body=fake_response)
        sess = transport.Transport()
        headers = {
            'User-Agent': 'fake-curl',
            'X-Random-Header': 'x-random-value',
        }
        params = {
            'detailed-arg-name': 'qaz11 wsx22+edc33',
            'ssh_config_dir': '~/myusername/.ssh',
        }
        resp = sess.post(
            self.TEST_URL,
            headers=headers,
            params=params,
            json=fake_record2,
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
        sess = transport.Transport()
        resp = sess.get(self.REDIRECT_CHAIN[-2])
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_post_keeps_correct_method(self):
        self.setup_redirects(method=httpretty.POST, status=301)
        sess = transport.Transport()
        resp = sess.post(self.REDIRECT_CHAIN[-2])
        self.assertResponseOK(resp, body=fake_response)

    @httpretty.activate
    def test_redirect_forever(self):
        self.setup_redirects()
        sess = transport.Transport()
        resp = sess.get(self.REDIRECT_CHAIN[0])
        self.assertResponseOK(resp)
        # Request history length is 1 less than the source chain due to the
        # last response not being a redirect and not added to the history.
        self.assertEqual(len(self.REDIRECT_CHAIN) - 1, len(resp.history))

    @httpretty.activate
    def test_no_redirect(self):
        self.setup_redirects()
        sess = transport.Transport(redirect=False)
        resp = sess.get(self.REDIRECT_CHAIN[0])
        self.assertEqual(305, resp.status_code)
        self.assertEqual(self.REDIRECT_CHAIN[0], resp.url)

    @httpretty.activate
    def test_redirect_limit(self):
        self.setup_redirects()
        for i in (1, 2):
            sess = transport.Transport(redirect=i)
            resp = sess.get(self.REDIRECT_CHAIN[0])
            self.assertResponseOK(resp, status=305, body=fake_redirect)
            self.assertEqual(self.REDIRECT_CHAIN[i], resp.url)

    @httpretty.activate
    def test_history_matches_requests(self):
        self.setup_redirects(status=301)
        sess = transport.Transport(redirect=True)
        req_resp = requests.get(
            self.REDIRECT_CHAIN[0],
            allow_redirects=True,
        )

        ses_resp = sess.get(self.REDIRECT_CHAIN[0])

        self.assertEqual(type(ses_resp.history), type(req_resp.history))
        self.assertEqual(len(ses_resp.history), len(req_resp.history))

        for r, s in zip(req_resp.history, ses_resp.history):
            self.assertEqual(s.url, r.url)
            self.assertEqual(s.status_code, r.status_code)
