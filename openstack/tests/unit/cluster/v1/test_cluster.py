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

import datetime

import mock
import testtools

from openstack.cluster.v1 import cluster


FAKE_ID = '092d0955-2645-461a-b8fa-6a44655cdb2c'
FAKE_NAME = 'test_cluster'

FAKE = {
    'desired_capacity': 1,
    'max_size': 3,
    'min_size': 0,
    'name': FAKE_NAME,
    'parent': None,
    'profile_id': 'myserver',
    'metadata': {},
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
        'parent': None,
        'policies': [],
        'profile_id': '560a8f9d-7596-4a32-85e8-03645fa7be13',
        'profile_name': 'myserver',
        'project': '333acb15a43242f4a609a27cb097a8f2',
        'status': 'INIT',
        'status_reason': 'Initializing',
        'timeout': None,
        'user': '6d600911ff764e54b309ce734c89595e',
    }
}


class TestCluster(testtools.TestCase):

    def setUp(self):
        super(TestCluster, self).setUp()

    def test_basic(self):
        sot = cluster.Cluster()
        self.assertEqual('cluster', sot.resource_key)
        self.assertEqual('clusters', sot.resources_key)
        self.assertEqual('/clusters', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = cluster.Cluster(FAKE)
        self.assertIsNone(sot.id)
        self.assertEqual(FAKE['name'], sot.name)

        self.assertEqual(FAKE['profile_id'], sot.profile_id)

        self.assertEqual(FAKE['min_size'], sot.min_size)
        self.assertEqual(FAKE['max_size'], sot.max_size)
        self.assertEqual(FAKE['desired_capacity'], sot.desired_capacity)

        self.assertEqual(FAKE['timeout'], sot.timeout)
        self.assertEqual(FAKE['metadata'], sot.metadata)

        dt = datetime.datetime(2015, 10, 10, 12, 46, 36, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.init_at.replace(tzinfo=None))
        dt = datetime.datetime(2015, 10, 10, 12, 46, 36, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        dt = datetime.datetime(2016, 10, 10, 12, 46, 36, 000000).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.updated_at.replace(tzinfo=None))

    def test_scale_in(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.scale_in(sess, 3))
        url = 'clusters/%s/actions' % sot.id
        body = {'scale_in': {'count': 3}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_scale_out(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.scale_out(sess, 3))
        url = 'clusters/%s/actions' % sot.id
        body = {'scale_out': {'count': 3}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_resize(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.resize(sess, foo='bar', zoo=5))
        url = 'clusters/%s/actions' % sot.id
        body = {'resize': {'foo': 'bar', 'zoo': 5}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_add_nodes(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.add_nodes(sess, ['node-33']))
        url = 'clusters/%s/actions' % sot.id
        body = {'add_nodes': {'nodes': ['node-33']}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_del_nodes(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.del_nodes(sess, ['node-11']))
        url = 'clusters/%s/actions' % sot.id
        body = {'del_nodes': {'nodes': ['node-11']}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_policy_attach(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

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
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_policy_detach(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.policy_detach(sess, 'POLICY'))

        url = 'clusters/%s/actions' % sot.id
        body = {'policy_detach': {'policy_id': 'POLICY'}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_policy_update(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

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
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_check(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.check(sess))
        url = 'clusters/%s/actions' % sot.id
        body = {'check': {}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_recover(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'

        resp = mock.Mock()
        resp.json = mock.Mock(return_value='')
        sess = mock.Mock()
        sess.post = mock.Mock(return_value=resp)
        self.assertEqual('', sot.recover(sess))
        url = 'clusters/%s/actions' % sot.id
        body = {'recover': {}}
        sess.post.assert_called_once_with(url, endpoint_filter=sot.service,
                                          json=body)

    def test_cluster_delete(self):
        sot = cluster.Cluster(FAKE)
        sot['id'] = 'IDENTIFIER'
        url = 'clusters/%s' % sot.id
        resp = mock.Mock(headers={'location': 'actions/fake_action'})
        sess = mock.Mock()
        sess.delete = mock.Mock(return_value=resp)
        clus = sot.delete(sess)
        self.assertEqual('actions/fake_action', clus.location)
        sess.delete.assert_called_once_with(url, endpoint_filter=sot.service)
