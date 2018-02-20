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
from openstack.tests.unit import base

from openstack.compute.v2 import service

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'binary': 'nova-compute',
    'host': 'host1',
    'status': 'enabled',
    'state': 'up',
    'zone': 'nova'
}


class TestService(base.TestCase):

    def setUp(self):
        super(TestService, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = service.Service()
        self.assertEqual('service', sot.resource_key)
        self.assertEqual('services', sot.resources_key)
        self.assertEqual('/os-services', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_get)

    def test_make_it(self):
        sot = service.Service(**EXAMPLE)
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['zone'], sot.zone)
        self.assertEqual(EXAMPLE['id'], sot.id)

    def test_force_down(self):
        sot = service.Service(**EXAMPLE)

        res = sot.force_down(self.sess, 'host1', 'nova-compute')
        self.assertIsNone(res.body)

        url = 'os-services/force-down'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
            'forced_down': True,
        }
        self.sess.put.assert_called_with(
            url, json=body)

    def test_enable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.enable(self.sess, 'host1', 'nova-compute')
        self.assertIsNone(res.body)

        url = 'os-services/enable'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
        }
        self.sess.put.assert_called_with(
            url, json=body)

    def test_disable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.disable(self.sess, 'host1', 'nova-compute')
        self.assertIsNone(res.body)

        url = 'os-services/disable'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
        }
        self.sess.put.assert_called_with(
            url, json=body)

    def test_disable_with_reason(self):
        sot = service.Service(**EXAMPLE)
        reason = 'fencing'

        res = sot.disable(self.sess, 'host1', 'nova-compute', reason=reason)

        self.assertIsNone(res.body)

        url = 'os-services/disable-log-reason'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
            'disabled_reason': reason
        }
        self.sess.put.assert_called_with(
            url, json=body)
