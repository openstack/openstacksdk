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

from openstack.clustering.v1 import cluster


FAKE_ID = '092d0955-2645-461a-b8fa-6a44655cdb2c'
FAKE_NAME = 'test_cluster'

FAKE = {
    'id': 'IDENTIFIER',
    'config': {'key1': 'value1', 'key2': 'value2'},
    'desired_capacity': 1,
    'max_size': 3,
    'min_size': 0,
    'name': FAKE_NAME,
    'profile_id': 'myserver',
    'profile_only': True,
    'metadata': {},
    'dependents': {},
    'timeout': None,
    'init_at': '2015-10-10T12:46:36.000000',
    'created_at': '2015-10-10T12:46:36.000000',
    'updated_at': '2016-10-10T12:46:36.000000',
}

FAKE_CREATE_RESP = {
    'cluster': {
        'action': 'a679c926-908f-49e7-a822-06ca371e64e1',
        'init_at': '2015-10-10T12:46:36.000000',
        'created_at': '2015-10-10T12:46:36.000000',
        'updated_at': '2016-10-10T12:46:36.000000',
        'data': {},
        'desired_capacity': 1,
        'domain': None,
        'id': FAKE_ID,
        'init_time': None,
        'max_size': 3,
        'metadata': {},
        'min_size': 0,
        'name': 'test_cluster',
        'nodes': [],
        'policies': [],
        'profile_id': '560a8f9d-7596-4a32-85e8-03645fa7be13',
        'profile_name': 'myserver',
        'project': '333acb15a43242f4a609a27cb097a8f2',
        'status': 'INIT',
        'status_reason': 'Initializing',
        'timeout': None,
        'user': '6d600911ff764e54b309ce734c89595e',
        'dependents': {},
    }
}


class TestCluster(base.TestCase):

    def setUp(self):
        super(TestCluster, self).setUp()

    def test_basic(self):
        sot = cluster.Cluster()
        self.assertEqual('cluster', sot.resource_key)
        self.assertEqual('clusters', sot.resources_key)
        self.assertEqual('/clusters', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = cluster.Cluster(**FAKE)

        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)

        self.assertEqual(FAKE['profile_id'], sot.profile_id)

        self.assertEqual(FAKE['min_size'], sot.min_size)
        self.assertEqual(FAKE['max_size'], sot.max_size)
        self.assertEqual(FAKE['desired_capacity'], sot.desired_capacity)

        self.assertEqual(FAKE['config'], sot.config)
        self.assertEqual(FAKE['timeout'], sot.timeout)
        self.assertEqual(FAKE['metadata'], sot.metadata)

        self.assertEqual(FAKE['init_at'], sot.init_at)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['dependents'], sot.dependents)
        self.assertTrue(sot.is_profile_only)

        self.assertDictEqual({"limit": "limit",
                              "marker": "marker",
                              "name": "name",
                              "status": "status",
                              "sort": "sort",
                              "global_project": "global_project"},
                             sot._query_mapping._mapping)

    def test_scale_in(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.scale_in(sess, 3))
        url = 'clusters/%s/actions' % sot.id
        body = {'scale_in': {'count': 3}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_scale_out(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.scale_out(sess, 3))
        url = 'clusters/%s/actions' % sot.id
        body = {'scale_out': {'count': 3}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_resize(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.resize(sess, foo='bar', zoo=5))
        url = 'clusters/%s/actions' % sot.id
        body = {'resize': {'foo': 'bar', 'zoo': 5}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_add_nodes(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.add_nodes(sess, ['node-33']))
        url = 'clusters/%s/actions' % sot.id
        body = {'add_nodes': {'nodes': ['node-33']}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_del_nodes(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.del_nodes(sess, ['node-11']))
        url = 'clusters/%s/actions' % sot.id
        body = {'del_nodes': {'nodes': ['node-11']}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_del_nodes_with_params(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        params = {
            'destroy_after_deletion': True,
        }
        self.assertEqual('', sot.del_nodes(sess, ['node-11'], **params))
        url = 'clusters/%s/actions' % sot.id
        body = {
            'del_nodes': {
                'nodes': ['node-11'],
                'destroy_after_deletion': True,
            }
        }
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_replace_nodes(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.replace_nodes(sess, {'node-22': 'node-44'}))
        url = 'clusters/%s/actions' % sot.id
        body = {'replace_nodes': {'nodes': {'node-22': 'node-44'}}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_policy_attach(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        params = {
            'enabled': True,
        }
        self.assertEqual('', sot.policy_attach(sess, 'POLICY', **params))

        url = 'clusters/%s/actions' % sot.id
        body = {
            'policy_attach': {
                'policy_id': 'POLICY',
                'enabled': True,
            }
        }
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_policy_detach(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.policy_detach(sess, 'POLICY'))

        url = 'clusters/%s/actions' % sot.id
        body = {'policy_detach': {'policy_id': 'POLICY'}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_policy_update(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        params = {
            'enabled': False
        }
        self.assertEqual('', sot.policy_update(sess, 'POLICY', **params))

        url = 'clusters/%s/actions' % sot.id
        body = {
            'policy_update': {
                'policy_id': 'POLICY',
                'enabled': False
            }
        }
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_check(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.check(sess))
        url = 'clusters/%s/actions' % sot.id
        body = {'check': {}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_recover(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.recover(sess))
        url = 'clusters/%s/actions' % sot.id
        body = {'recover': {}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_operation(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.op(sess, 'dance', style='tango'))
        url = 'clusters/%s/ops' % sot.id
        body = {'dance': {'style': 'tango'}}
        sess.post.assert_called_once_with(url,
                                          json=body)

    def test_force_delete(self):
        sot = cluster.Cluster(**FAKE)

        resp = mock.Mock()
        resp.headers = {}
        resp.json = mock.Mock(return_value={"foo": "bar"})
        resp.status_code = 200
        sess = mock.Mock()
        sess.delete = mock.Mock(return_value=resp)

        res = sot.force_delete(sess)
        self.assertEqual(sot, res)
        url = 'clusters/%s' % sot.id
        body = {'force': True}
        sess.delete.assert_called_once_with(url, json=body)
