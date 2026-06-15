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

from openstack.block_storage.v3 import cluster
from openstack.tests.unit import base

EXAMPLE = {
    "binary": "cinder-volume",
    "name": "cluster_name",
    "state": "up",
    "status": "enabled",
    "replication_status": None,
    "num_hosts": 3,
    "num_down_hosts": 0,
    "last_heartbeat": "2017-06-29T05:50:35.000000",
    "created_at": "2017-06-29T05:50:35.000000",
    "updated_at": "2017-06-29T05:50:35.000000",
    "disabled_reason": None,
    "frozen": False,
    "active_backend_id": None,
}


class TestCluster(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value={'cluster': {}})
        self.resp.status_code = 200
        self.resp.headers = {}
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = '3.7'

    def test_basic(self):
        sot = cluster.Cluster()
        self.assertEqual('cluster', sot.resource_key)
        self.assertEqual('clusters', sot.resources_key)
        self.assertEqual('/clusters', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

        self.assertDictEqual(
            {
                'active_backend_id': 'active_backend_id',
                'binary': 'binary',
                'disabled': 'disabled',
                'frozen': 'frozen',
                'is_up': 'is_up',
                'limit': 'limit',
                'marker': 'marker',
                'name': 'name',
                'num_down_hosts': 'num_down_hosts',
                'num_hosts': 'num_hosts',
                'replication_status': 'replication_status',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = cluster.Cluster(**EXAMPLE)
        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['replication_status'], sot.replication_status)
        self.assertEqual(EXAMPLE['num_hosts'], sot.num_hosts)
        self.assertEqual(EXAMPLE['num_down_hosts'], sot.num_down_hosts)
        self.assertEqual(EXAMPLE['last_heartbeat'], sot.last_heartbeat)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['disabled_reason'], sot.disabled_reason)
        self.assertEqual(EXAMPLE['frozen'], sot.frozen)
        self.assertEqual(EXAMPLE['active_backend_id'], sot.active_backend_id)

    def test_enable(self):
        sot = cluster.Cluster(**EXAMPLE)

        res = sot.enable(self.sess)
        self.assertIsNotNone(res)

        url = 'clusters/enable'
        body = {
            'name': 'cluster_name',
            'binary': 'cinder-volume',
        }
        self.sess.put.assert_called_with(
            url,
            json=body,
            microversion=self.sess.default_microversion,
        )

    def test_disable(self):
        sot = cluster.Cluster(**EXAMPLE)

        res = sot.disable(self.sess)
        self.assertIsNotNone(res)

        url = 'clusters/disable'
        body = {
            'name': 'cluster_name',
            'binary': 'cinder-volume',
        }
        self.sess.put.assert_called_with(
            url,
            json=body,
            microversion=self.sess.default_microversion,
        )

    def test_disable__with_reason(self):
        sot = cluster.Cluster(**EXAMPLE)
        reason = 'for testing'

        res = sot.disable(self.sess, reason=reason)
        self.assertIsNotNone(res)

        url = 'clusters/disable'
        body = {
            'name': 'cluster_name',
            'binary': 'cinder-volume',
            'disabled_reason': reason,
        }
        self.sess.put.assert_called_with(
            url,
            json=body,
            microversion=self.sess.default_microversion,
        )
