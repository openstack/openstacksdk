# Copyright 2017 OVH SAS
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from shade import exc
from shade.tests.unit import base


class TestQosPolicy(base.RequestsMockTestCase):

    policy_name = 'qos test policy'
    policy_id = '881d1bb7-a663-44c0-8f9f-ee2765b74486'
    project_id = 'c88fc89f-5121-4a4c-87fd-496b5af864e9'

    mock_policy = {
        'id': policy_id,
        'name': policy_name,
        'description': '',
        'rules': [],
        'project_id': project_id,
        'tenant_id': project_id,
        'shared': False,
        'is_default': False
    }

    def test_get_qos_policy(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]})
        ])
        r = self.cloud.get_qos_policy(self.policy_name)
        self.assertIsNotNone(r)
        self.assertDictEqual(self.mock_policy, r)
        self.assert_calls()

    def test_create_qos_policy(self):
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policy': self.mock_policy})
        ])
        policy = self.cloud.create_qos_policy(
            name=self.policy_name, project_id=self.project_id)
        self.assertDictEqual(self.mock_policy, policy)
        self.assert_calls()

    def test_delete_qos_policy(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies',
                             '%s.json' % self.policy_id]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_qos_policy(self.policy_name))
        self.assert_calls()

    def test_delete_qos_policy_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': []})
        ])
        self.assertFalse(self.cloud.delete_qos_policy('goofy'))
        self.assert_calls()

    def test_delete_qos_policy_multiple_found(self):
        policy1 = dict(id='123', name=self.policy_name)
        policy2 = dict(id='456', name=self.policy_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [policy1, policy2]})
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.delete_qos_policy,
                          self.policy_name)
        self.assert_calls()

    def test_delete_qos_policy_multiple_using_id(self):
        policy1 = self.mock_policy
        policy2 = dict(id='456', name=self.policy_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [policy1, policy2]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies',
                             '%s.json' % self.policy_id]),
                 json={})
        ])
        self.assertTrue(self.cloud.delete_qos_policy(policy1['id']))
        self.assert_calls()

    def test_update_qos_policy(self):
        expected_policy = copy.copy(self.mock_policy)
        expected_policy['name'] = 'goofy'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies',
                             '%s.json' % self.policy_id]),
                 json={'policy': expected_policy},
                 validate=dict(
                     json={'policy': {'name': 'goofy'}}))
        ])
        policy = self.cloud.update_qos_policy(
            self.policy_id, policy_name='goofy')
        self.assertDictEqual(expected_policy, policy)
        self.assert_calls()
