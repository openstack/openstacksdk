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

import copy
import testtools

from openstack.cloud import exc
from openstack.tests.unit import base


CLUSTERING_DICT = {
    'name': 'fake-name',
    'profile_id': '1',
    'desired_capacity': 1,
    'config': 'fake-config',
    'max_size': 1,
    'min_size': 1,
    'timeout': 100,
    'metadata': {}
}

PROFILE_DICT = {
    'name': 'fake-profile-name',
    'spec': {},
    'metadata': {}
}

POLICY_DICT = {
    'name': 'fake-profile-name',
    'spec': {},
}

RECEIVER_DICT = {
    'action': 'FAKE_CLUSTER_ACTION',
    'cluster_id': 'fake-cluster-id',
    'name': 'fake-receiver-name',
    'params': {},
    'type': 'webhook'
}

NEW_CLUSTERING_DICT = copy.copy(CLUSTERING_DICT)
NEW_CLUSTERING_DICT['id'] = '1'
NEW_PROFILE_DICT = copy.copy(PROFILE_DICT)
NEW_PROFILE_DICT['id'] = '1'
NEW_POLICY_DICT = copy.copy(POLICY_DICT)
NEW_POLICY_DICT['id'] = '1'
NEW_RECEIVER_DICT = copy.copy(RECEIVER_DICT)
NEW_RECEIVER_DICT['id'] = '1'


class TestClustering(base.TestCase):

    def assertAreInstances(self, elements, elem_type):
        for e in elements:
            self.assertIsInstance(e, elem_type)

    def setUp(self):
        super(TestClustering, self).setUp()
        self.use_senlin()

    def test_create_cluster(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles', '1']),
                 json={
                     "profiles": [NEW_PROFILE_DICT]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles']),
                 json={
                     "profiles": [NEW_PROFILE_DICT]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 json=NEW_CLUSTERING_DICT)
        ])
        profile = self.cloud.get_cluster_profile_by_id(NEW_PROFILE_DICT['id'])
        c = self.cloud.create_cluster(
            name=CLUSTERING_DICT['name'],
            desired_capacity=CLUSTERING_DICT['desired_capacity'],
            profile=profile,
            config=CLUSTERING_DICT['config'],
            max_size=CLUSTERING_DICT['max_size'],
            min_size=CLUSTERING_DICT['min_size'],
            metadata=CLUSTERING_DICT['metadata'],
            timeout=CLUSTERING_DICT['timeout'])

        self.assertEqual(NEW_CLUSTERING_DICT, c)
        self.assert_calls()

    def test_create_cluster_exception(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles', '1']),
                 json={
                     "profiles": [NEW_PROFILE_DICT]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles']),
                 json={
                     "profiles": [NEW_PROFILE_DICT]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 status_code=500)
        ])
        profile = self.cloud.get_cluster_profile_by_id(NEW_PROFILE_DICT['id'])
        with testtools.ExpectedException(
                exc.OpenStackCloudHTTPError,
                "Error creating cluster fake-name.*"):
            self.cloud.create_cluster(name='fake-name', profile=profile)
        self.assert_calls()

    def test_get_cluster_by_id(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json={
                     "cluster": NEW_CLUSTERING_DICT})
        ])
        cluster = self.cloud.get_cluster_by_id('1')
        self.assertEqual(cluster['id'], '1')
        self.assert_calls()

    def test_get_cluster_not_found_returns_false(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters',
                                                     'no-cluster']),
                 status_code=404)
        ])
        c = self.cloud.get_cluster_by_id('no-cluster')
        self.assertFalse(c)
        self.assert_calls()

    def test_update_cluster(self):
        new_max_size = 5
        updated_cluster = copy.copy(NEW_CLUSTERING_DICT)
        updated_cluster['max_size'] = new_max_size
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json={
                     "cluster": NEW_CLUSTERING_DICT}),
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json=updated_cluster,
                 )
        ])
        cluster = self.cloud.get_cluster_by_id('1')
        c = self.cloud.update_cluster(cluster, new_max_size)
        self.assertEqual(updated_cluster, c)
        self.assert_calls()

    def test_delete_cluster(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 json={
                     "clusters": [NEW_CLUSTERING_DICT]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1',
                                                     'policies']),
                 json={"cluster_policies": []}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers']),
                 json={"receivers": []}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json=NEW_CLUSTERING_DICT)
        ])
        self.assertTrue(self.cloud.delete_cluster('1'))
        self.assert_calls()

    def test_list_clusters(self):
        clusters = {'clusters': [NEW_CLUSTERING_DICT]}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 json=clusters)
        ])
        c = self.cloud.list_clusters()

        self.assertIsInstance(c, list)
        self.assertAreInstances(c, dict)

        self.assert_calls()

    def test_attach_policy_to_cluster(self):
        policy = {
            'policy_id': '1',
            'enabled': 'true'
        }
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json={
                     "cluster": NEW_CLUSTERING_DICT}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies', '1']),
                 json={
                     "policy": NEW_POLICY_DICT}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1',
                                                     'actions']),
                 json={'policy_attach': policy})
        ])
        cluster = self.cloud.get_cluster_by_id('1')
        policy = self.cloud.get_cluster_policy_by_id('1')
        p = self.cloud.attach_policy_to_cluster(cluster, policy, 'true')
        self.assertTrue(p)
        self.assert_calls()

    def test_detach_policy_from_cluster(self):
        updated_cluster = copy.copy(NEW_CLUSTERING_DICT)
        updated_cluster['policies'] = ['1']
        detached_cluster = copy.copy(NEW_CLUSTERING_DICT)
        detached_cluster['policies'] = []

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json={
                     "cluster": NEW_CLUSTERING_DICT}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies', '1']),
                 json={
                     "policy": NEW_POLICY_DICT}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1',
                                                     'actions']),
                 json={'policy_detach': {'policy_id': '1'}}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json={
                     "cluster": updated_cluster}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json={
                     "cluster": detached_cluster}),
        ])
        cluster = self.cloud.get_cluster_by_id('1')
        policy = self.cloud.get_cluster_policy_by_id('1')
        p = self.cloud.detach_policy_from_cluster(cluster, policy, wait=True)
        self.assertTrue(p)
        self.assert_calls()

    def test_get_policy_on_cluster_by_id(self):
        cluster_policy = {
            "cluster_id": "1",
            "cluster_name": "cluster1",
            "enabled": True,
            "id": "1",
            "policy_id": "1",
            "policy_name": "policy1",
            "policy_type": "senlin.policy.deletion-1.0"
        }

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1',
                                                     'policies', '1']),
                 json={
                     "cluster_policy": cluster_policy})
        ])
        policy = self.cloud.get_policy_on_cluster('1', '1')
        self.assertEqual(policy['cluster_id'], '1')
        self.assert_calls()

    def test_get_policy_on_cluster_not_found_returns_false(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1',
                                                     'policies', 'no-policy']),
                 status_code=404)
        ])
        p = self.cloud.get_policy_on_cluster('1', 'no-policy')
        self.assertFalse(p)
        self.assert_calls()

    def test_update_policy_on_cluster(self):
        policy = {
            'policy_id': '1',
            'enabled': 'true'
        }
        updated_cluster = copy.copy(NEW_CLUSTERING_DICT)
        updated_cluster['policies'] = policy
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1']),
                 json={
                     "cluster": NEW_CLUSTERING_DICT}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies',
                                                     '1']),
                 json={
                     "policy": NEW_POLICY_DICT}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1',
                                                     'actions']),
                 json={'policies': []})
        ])
        cluster = self.cloud.get_cluster_by_id('1')
        policy = self.cloud.get_cluster_policy_by_id('1')
        p = self.cloud.update_policy_on_cluster(cluster, policy, True)
        self.assertTrue(p)
        self.assert_calls()

    def test_get_policy_on_cluster(self):
        cluster_policy = {
            'cluster_id': '1',
            'cluster_name': 'cluster1',
            'enabled': 'true',
            'id': '1',
            'policy_id': '1',
            'policy_name': 'policy1',
            'policy_type': 'type'
        }

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters', '1',
                                                     'policies', '1']),
                 json={
                     "cluster_policy": cluster_policy})
        ])
        get_policy = self.cloud.get_policy_on_cluster('1', '1')
        self.assertEqual(get_policy, cluster_policy)
        self.assert_calls()

    def test_create_cluster_profile(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles']),
                 json={'profile': NEW_PROFILE_DICT})
        ])
        p = self.cloud.create_cluster_profile('fake-profile-name', {})

        self.assertEqual(NEW_PROFILE_DICT, p)
        self.assert_calls()

    def test_create_cluster_profile_exception(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles']),
                 status_code=500)
        ])
        with testtools.ExpectedException(
                exc.OpenStackCloudHTTPError,
                "Error creating profile fake-profile-name.*"):
            self.cloud.create_cluster_profile('fake-profile-name', {})
        self.assert_calls()

    def test_list_cluster_profiles(self):
        profiles = {'profiles': [NEW_PROFILE_DICT]}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles']),
                 json=profiles)
        ])
        p = self.cloud.list_cluster_profiles()

        self.assertIsInstance(p, list)
        self.assertAreInstances(p, dict)

        self.assert_calls()

    def test_get_cluster_profile_by_id(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles', '1']),
                 json={
                     "profile": NEW_PROFILE_DICT})
        ])
        p = self.cloud.get_cluster_profile_by_id('1')
        self.assertEqual(p['id'], '1')
        self.assert_calls()

    def test_get_cluster_profile_not_found_returns_false(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles',
                                                     'no-profile']),
                 status_code=404)
        ])
        p = self.cloud.get_cluster_profile_by_id('no-profile')
        self.assertFalse(p)
        self.assert_calls()

    def test_update_cluster_profile(self):
        new_name = "new-name"
        updated_profile = copy.copy(NEW_PROFILE_DICT)
        updated_profile['name'] = new_name
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles']),
                 json={
                     "profiles": [NEW_PROFILE_DICT]}),
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles', '1']),
                 json=updated_profile,
                 )
        ])
        p = self.cloud.update_cluster_profile('1', new_name=new_name)
        self.assertEqual(updated_profile, p)
        self.assert_calls()

    def test_delete_cluster_profile(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles', '1']),
                 json={
                     "profile": NEW_PROFILE_DICT}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 json={}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'profiles', '1']),
                 json=NEW_PROFILE_DICT)
        ])
        profile = self.cloud.get_cluster_profile_by_id('1')
        self.assertTrue(self.cloud.delete_cluster_profile(profile))
        self.assert_calls()

    def test_create_cluster_policy(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies']),
                 json={'policy': NEW_POLICY_DICT})
        ])
        p = self.cloud.create_cluster_policy('fake-policy-name', {})

        self.assertEqual(NEW_POLICY_DICT, p)
        self.assert_calls()

    def test_create_cluster_policy_exception(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies']),
                 status_code=500)
        ])
        with testtools.ExpectedException(
                exc.OpenStackCloudHTTPError,
                "Error creating policy fake-policy-name.*"):
            self.cloud.create_cluster_policy('fake-policy-name', {})
        self.assert_calls()

    def test_list_cluster_policies(self):
        policies = {'policies': [NEW_POLICY_DICT]}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies']),
                 json=policies)
        ])
        p = self.cloud.list_cluster_policies()

        self.assertIsInstance(p, list)
        self.assertAreInstances(p, dict)

        self.assert_calls()

    def test_get_cluster_policy_by_id(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies', '1']),
                 json={
                     "policy": NEW_POLICY_DICT})
        ])
        p = self.cloud.get_cluster_policy_by_id('1')
        self.assertEqual(p['id'], '1')
        self.assert_calls()

    def test_get_cluster_policy_not_found_returns_false(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies',
                                                     'no-policy']),
                 status_code=404)
        ])
        p = self.cloud.get_cluster_policy_by_id('no-policy')
        self.assertFalse(p)
        self.assert_calls()

    def test_update_cluster_policy(self):
        new_name = "new-name"
        updated_policy = copy.copy(NEW_POLICY_DICT)
        updated_policy['name'] = new_name
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies']),
                 json={
                     "policies": [NEW_POLICY_DICT]}),
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies', '1']),
                 json=updated_policy,
                 )
        ])
        p = self.cloud.update_cluster_policy('1', new_name=new_name)
        self.assertEqual(updated_policy, p)
        self.assert_calls()

    def test_delete_cluster_policy(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies', '1']),
                 json={
                     "policy": NEW_POLICY_DICT}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 json={}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'policies', '1']),
                 json=NEW_POLICY_DICT)
        ])
        self.assertTrue(self.cloud.delete_cluster_policy('1'))
        self.assert_calls()

    def test_create_cluster_receiver(self):
        clusters = {'clusters': [NEW_CLUSTERING_DICT]}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 json=clusters),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers']),
                 json={'receiver': NEW_RECEIVER_DICT})
        ])
        r = self.cloud.create_cluster_receiver('fake-receiver-name', {})

        self.assertEqual(NEW_RECEIVER_DICT, r)
        self.assert_calls()

    def test_create_cluster_receiver_exception(self):
        clusters = {'clusters': [NEW_CLUSTERING_DICT]}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'clusters']),
                 json=clusters),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers']),
                 status_code=500),
        ])
        with testtools.ExpectedException(
                exc.OpenStackCloudHTTPError,
                "Error creating receiver fake-receiver-name.*"):
            self.cloud.create_cluster_receiver('fake-receiver-name', {})
        self.assert_calls()

    def test_list_cluster_receivers(self):
        receivers = {'receivers': [NEW_RECEIVER_DICT]}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers']),
                 json=receivers)
        ])
        r = self.cloud.list_cluster_receivers()

        self.assertIsInstance(r, list)
        self.assertAreInstances(r, dict)

        self.assert_calls()

    def test_get_cluster_receiver_by_id(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers', '1']),
                 json={
                     "receiver": NEW_RECEIVER_DICT})
        ])
        r = self.cloud.get_cluster_receiver_by_id('1')
        self.assertEqual(r['id'], '1')
        self.assert_calls()

    def test_get_cluster_receiver_not_found_returns_false(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers',
                                                     'no-receiver']),
                 json={'receivers': []})
        ])
        p = self.cloud.get_cluster_receiver_by_id('no-receiver')
        self.assertFalse(p)
        self.assert_calls()

    def test_update_cluster_receiver(self):
        new_name = "new-name"
        updated_receiver = copy.copy(NEW_RECEIVER_DICT)
        updated_receiver['name'] = new_name
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers']),
                 json={
                     "receivers": [NEW_RECEIVER_DICT]}),
            dict(method='PATCH',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers', '1']),
                 json=updated_receiver,
                 )
        ])
        r = self.cloud.update_cluster_receiver('1', new_name=new_name)
        self.assertEqual(updated_receiver, r)
        self.assert_calls()

    def test_delete_cluster_receiver(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers']),
                 json={
                     "receivers": [NEW_RECEIVER_DICT]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers', '1']),
                 json=NEW_RECEIVER_DICT),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'clustering', 'public', append=['v1', 'receivers', '1']),
                 json={}),
        ])
        self.assertTrue(self.cloud.delete_cluster_receiver('1', wait=True))
        self.assert_calls()
