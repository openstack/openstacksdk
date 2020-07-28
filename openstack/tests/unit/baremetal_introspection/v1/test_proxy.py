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

from unittest import mock

from keystoneauth1 import adapter

from openstack.baremetal.v1 import node as _node
from openstack.baremetal_introspection.v1 import _proxy
from openstack.baremetal_introspection.v1 import introspection
from openstack import exceptions
from openstack.tests.unit import base
from openstack.tests.unit import test_proxy_base


@mock.patch.object(introspection.Introspection, 'create', autospec=True)
class TestStartIntrospection(base.TestCase):

    def setUp(self):
        super(TestStartIntrospection, self).setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.proxy = _proxy.Proxy(self.session)

    def test_create_introspection(self, mock_create):
        self.proxy.start_introspection('abcd')
        mock_create.assert_called_once_with(mock.ANY, self.proxy)
        introspect = mock_create.call_args[0][0]
        self.assertEqual('abcd', introspect.id)

    def test_create_introspection_with_node(self, mock_create):
        self.proxy.start_introspection(_node.Node(id='abcd'))
        mock_create.assert_called_once_with(mock.ANY, self.proxy)
        introspect = mock_create.call_args[0][0]
        self.assertEqual('abcd', introspect.id)

    def test_create_introspection_manage_boot(self, mock_create):
        self.proxy.start_introspection('abcd', manage_boot=False)
        mock_create.assert_called_once_with(mock.ANY, self.proxy,
                                            manage_boot=False)
        introspect = mock_create.call_args[0][0]
        self.assertEqual('abcd', introspect.id)


class TestBaremetalIntrospectionProxy(test_proxy_base.TestProxyBase):

    def setUp(self):
        super(TestBaremetalIntrospectionProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_get_introspection(self):
        self.verify_get(self.proxy.get_introspection,
                        introspection.Introspection)


@mock.patch('time.sleep', lambda _sec: None)
@mock.patch.object(introspection.Introspection, 'fetch', autospec=True)
class TestWaitForIntrospection(base.TestCase):

    def setUp(self):
        super(TestWaitForIntrospection, self).setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.proxy = _proxy.Proxy(self.session)
        self.fake = {'state': 'waiting', 'error': None, 'finished': False}
        self.introspection = introspection.Introspection(**self.fake)

    def test_already_finished(self, mock_fetch):
        self.introspection.is_finished = True
        self.introspection.state = 'finished'
        result = self.proxy.wait_for_introspection(self.introspection)
        self.assertIs(result, self.introspection)
        self.assertFalse(mock_fetch.called)

    def test_wait(self, mock_fetch):
        marker = [False]  # mutable object to modify in the closure

        def _side_effect(allocation, session):
            if marker[0]:
                self.introspection.state = 'finished'
                self.introspection.is_finished = True
            else:
                self.introspection.state = 'processing'
                marker[0] = True

        mock_fetch.side_effect = _side_effect
        result = self.proxy.wait_for_introspection(self.introspection)
        self.assertIs(result, self.introspection)
        self.assertEqual(2, mock_fetch.call_count)

    def test_timeout(self, mock_fetch):
        self.assertRaises(exceptions.ResourceTimeout,
                          self.proxy.wait_for_introspection,
                          self.introspection,
                          timeout=0.001)
        mock_fetch.assert_called_with(self.introspection, self.proxy)

    def test_failure(self, mock_fetch):
        def _side_effect(allocation, session):
            self.introspection.state = 'error'
            self.introspection.is_finished = True
            self.introspection.error = 'boom'

        mock_fetch.side_effect = _side_effect
        self.assertRaisesRegex(exceptions.ResourceFailure, 'boom',
                               self.proxy.wait_for_introspection,
                               self.introspection)
        mock_fetch.assert_called_once_with(self.introspection, self.proxy)

    def test_failure_ignored(self, mock_fetch):
        def _side_effect(allocation, session):
            self.introspection.state = 'error'
            self.introspection.is_finished = True
            self.introspection.error = 'boom'

        mock_fetch.side_effect = _side_effect
        result = self.proxy.wait_for_introspection(self.introspection,
                                                   ignore_error=True)
        self.assertIs(result, self.introspection)
        mock_fetch.assert_called_once_with(self.introspection, self.proxy)


@mock.patch.object(_proxy.Proxy, 'request', autospec=True)
class TestAbortIntrospection(base.TestCase):

    def setUp(self):
        super(TestAbortIntrospection, self).setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.proxy = _proxy.Proxy(self.session)
        self.fake = {'id': '1234', 'finished': False}
        self.introspection = introspection.Introspection(**self.fake)

    def test_abort(self, mock_request):
        mock_request.return_value.status_code = 202
        self.proxy.abort_introspection(self.introspection)
        mock_request.assert_called_once_with(
            self.proxy, 'introspection/1234/abort', 'POST',
            headers=mock.ANY, microversion=mock.ANY,
            retriable_status_codes=[409, 503])


@mock.patch.object(_proxy.Proxy, 'request', autospec=True)
class TestGetData(base.TestCase):

    def setUp(self):
        super(TestGetData, self).setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.proxy = _proxy.Proxy(self.session)
        self.fake = {'id': '1234', 'finished': False}
        self.introspection = introspection.Introspection(**self.fake)

    def test_get_data(self, mock_request):
        mock_request.return_value.status_code = 200
        data = self.proxy.get_introspection_data(self.introspection)
        mock_request.assert_called_once_with(
            self.proxy, 'introspection/1234/data', 'GET',
            headers=mock.ANY, microversion=mock.ANY)
        self.assertIs(data, mock_request.return_value.json.return_value)

    def test_get_unprocessed_data(self, mock_request):
        mock_request.return_value.status_code = 200
        data = self.proxy.get_introspection_data(self.introspection,
                                                 processed=False)
        mock_request.assert_called_once_with(
            self.proxy, 'introspection/1234/data/unprocessed', 'GET',
            headers=mock.ANY, microversion='1.17')
        self.assertIs(data, mock_request.return_value.json.return_value)
