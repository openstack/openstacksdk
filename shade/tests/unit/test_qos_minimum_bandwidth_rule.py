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


class TestQosMinimumBandwidthRule(base.RequestsMockTestCase):

    policy_name = 'qos test policy'
    policy_id = '881d1bb7-a663-44c0-8f9f-ee2765b74486'
    project_id = 'c88fc89f-5121-4a4c-87fd-496b5af864e9'

    rule_id = 'ed1a2b05-0ad7-45d7-873f-008b575a02b3'
    rule_min_kbps = 1000

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

    mock_rule = {
        'id': rule_id,
        'min_kbps': rule_min_kbps,
        'direction': 'egress'
    }

    qos_extension = {
        "updated": "2015-06-08T10:00:00-00:00",
        "name": "Quality of Service",
        "links": [],
        "alias": "qos",
        "description": "The Quality of Service extension."
    }

    enabled_neutron_extensions = [qos_extension]

    def test_get_qos_minimum_bandwidth_rule(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'minimum_bandwidth_rules',
                             '%s.json' % self.rule_id]),
                 json={'minimum_bandwidth_rule': self.mock_rule})
        ])
        r = self.cloud.get_qos_minimum_bandwidth_rule(self.policy_name,
                                                      self.rule_id)
        self.assertDictEqual(self.mock_rule, r)
        self.assert_calls()

    def test_get_qos_minimum_bandwidth_rule_no_qos_policy_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudResourceNotFound,
            self.cloud.get_qos_minimum_bandwidth_rule,
            self.policy_name, self.rule_id)
        self.assert_calls()

    def test_get_qos_minimum_bandwidth_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.get_qos_minimum_bandwidth_rule,
            self.policy_name, self.rule_id)
        self.assert_calls()

    def test_create_qos_minimum_bandwidth_rule(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'minimum_bandwidth_rules']),
                 json={'minimum_bandwidth_rule': self.mock_rule})
        ])
        rule = self.cloud.create_qos_minimum_bandwidth_rule(
            self.policy_name, min_kbps=self.rule_min_kbps)
        self.assertDictEqual(self.mock_rule, rule)
        self.assert_calls()

    def test_create_qos_minimum_bandwidth_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_qos_minimum_bandwidth_rule, self.policy_name,
            min_kbps=100)
        self.assert_calls()

    def test_update_qos_minimum_bandwidth_rule(self):
        expected_rule = copy.copy(self.mock_rule)
        expected_rule['min_kbps'] = self.rule_min_kbps + 100
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'minimum_bandwidth_rules',
                             '%s.json' % self.rule_id]),
                 json={'minimum_bandwidth_rule': self.mock_rule}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'minimum_bandwidth_rules',
                             '%s.json' % self.rule_id]),
                 json={'minimum_bandwidth_rule': expected_rule},
                 validate=dict(
                     json={'minimum_bandwidth_rule': {
                           'min_kbps': self.rule_min_kbps + 100}}))
        ])
        rule = self.cloud.update_qos_minimum_bandwidth_rule(
            self.policy_id, self.rule_id, min_kbps=self.rule_min_kbps + 100)
        self.assertDictEqual(expected_rule, rule)
        self.assert_calls()

    def test_update_qos_minimum_bandwidth_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.update_qos_minimum_bandwidth_rule,
            self.policy_id, self.rule_id, min_kbps=2000)
        self.assert_calls()

    def test_delete_qos_minimum_bandwidth_rule(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'minimum_bandwidth_rules',
                             '%s.json' % self.rule_id]),
                 json={})
        ])
        self.assertTrue(
            self.cloud.delete_qos_minimum_bandwidth_rule(
                self.policy_name, self.rule_id))
        self.assert_calls()

    def test_delete_qos_minimum_bandwidth_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.delete_qos_minimum_bandwidth_rule,
            self.policy_name, self.rule_id)
        self.assert_calls()

    def test_delete_qos_minimum_bandwidth_rule_not_found(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': self.enabled_neutron_extensions}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'minimum_bandwidth_rules',
                             '%s.json' % self.rule_id]),
                 status_code=404)
        ])
        self.assertFalse(
            self.cloud.delete_qos_minimum_bandwidth_rule(
                self.policy_name, self.rule_id))
        self.assert_calls()
