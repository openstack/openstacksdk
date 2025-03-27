# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

from openstack.block_storage.v2 import service
from openstack.tests.unit import base

EXAMPLE = {
    "binary": "cinder-scheduler",
    "disabled_reason": None,
    "host": "devstack",
    "state": "up",
    "status": "enabled",
    "updated_at": "2017-06-29T05:50:35.000000",
    "zone": "nova",
}


class TestService(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None  # nothing uses this
        self.resp.json = mock.Mock(return_value={'service': {}})
        self.resp.status_code = 200
        self.resp.headers = {}
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = service.Service()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('services', sot.resources_key)
        self.assertEqual('/os-services', sot.base_path)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_delete)

        self.assertDictEqual(
            {
                'binary': 'binary',
                'host': 'host',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = service.Service(**EXAMPLE)
        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['binary'], sot.name)
        self.assertEqual(EXAMPLE['disabled_reason'], sot.disabled_reason)
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['zone'], sot.availability_zone)

    def test_enable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.enable(self.sess)
        self.assertIsNotNone(res)

        url = 'os-services/enable'
        body = {
            'binary': 'cinder-scheduler',
            'host': 'devstack',
        }
        self.sess.put.assert_called_with(url, json=body)

    def test_disable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.disable(self.sess)
        self.assertIsNotNone(res)

        url = 'os-services/disable'
        body = {
            'binary': 'cinder-scheduler',
            'host': 'devstack',
        }
        self.sess.put.assert_called_with(url, json=body)

    def test_disable__with_reason(self):
        sot = service.Service(**EXAMPLE)
        reason = 'fencing'

        res = sot.disable(self.sess, reason=reason)

        self.assertIsNotNone(res)

        url = 'os-services/disable-log-reason'
        body = {
            'binary': 'cinder-scheduler',
            'host': 'devstack',
            'disabled_reason': reason,
        }
        self.sess.put.assert_called_with(url, json=body)

    def test_thaw(self):
        sot = service.Service(**EXAMPLE)

        res = sot.thaw(self.sess)
        self.assertIsNotNone(res)

        url = 'os-services/thaw'
        body = {'host': 'devstack'}
        self.sess.put.assert_called_with(url, json=body)

    def test_freeze(self):
        sot = service.Service(**EXAMPLE)

        res = sot.freeze(self.sess)
        self.assertIsNotNone(res)

        url = 'os-services/freeze'
        body = {'host': 'devstack'}
        self.sess.put.assert_called_with(url, json=body)

    def test_failover(self):
        sot = service.Service(**EXAMPLE)

        res = sot.failover(self.sess)
        self.assertIsNotNone(res)

        url = 'os-services/failover_host'
        body = {'host': 'devstack'}
        self.sess.put.assert_called_with(url, json=body)
