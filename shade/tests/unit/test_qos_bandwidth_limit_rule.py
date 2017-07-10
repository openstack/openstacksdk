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


class TestQosBandwidthLimitRule(base.RequestsMockTestCase):

    policy_name = 'qos test policy'
    policy_id = '881d1bb7-a663-44c0-8f9f-ee2765b74486'
    project_id = 'c88fc89f-5121-4a4c-87fd-496b5af864e9'

    rule_id = 'ed1a2b05-0ad7-45d7-873f-008b575a02b3'
    rule_max_kbps = 1000
    rule_max_burst = 100

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
        'max_kbps': rule_max_kbps,
        'max_burst_kbps': rule_max_burst,
        'direction': 'egress'
    }

    qos_extension = {
        "updated": "2015-06-08T10:00:00-00:00",
        "name": "Quality of Service",
        "links": [],
        "alias": "qos",
        "description": "The Quality of Service extension."
    }

    qos_bw_limit_direction_extension = {
        "updated": "2017-04-10T10:00:00-00:00",
        "name": "Direction for QoS bandwidth limit rule",
        "links": [],
        "alias": "qos-bw-limit-direction",
        "description": ("Allow to configure QoS bandwidth limit rule with "
                        "specific direction: ingress or egress")
    }

    enabled_neutron_extensions = [qos_extension,
                                  qos_bw_limit_direction_extension]

    def test_get_qos_bandwidth_limit_rule(self):
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
                             'bandwidth_limit_rules',
                             '%s.json' % self.rule_id]),
                 json={'bandwidth_limit_rule': self.mock_rule})
        ])
        r = self.cloud.get_qos_bandwidth_limit_rule(self.policy_name,
                                                    self.rule_id)
        self.assertDictEqual(self.mock_rule, r)
        self.assert_calls()

    def test_get_qos_bandwidth_limit_rule_no_qos_policy_found(self):
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
            self.cloud.get_qos_bandwidth_limit_rule,
            self.policy_name, self.rule_id)
        self.assert_calls()

    def test_get_qos_bandwidth_limit_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.get_qos_bandwidth_limit_rule,
            self.policy_name, self.rule_id)
        self.assert_calls()

    def test_create_qos_bandwidth_limit_rule(self):
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
                             'bandwidth_limit_rules']),
                 json={'bandwidth_limit_rule': self.mock_rule})
        ])
        rule = self.cloud.create_qos_bandwidth_limit_rule(
            self.policy_name, max_kbps=self.rule_max_kbps)
        self.assertDictEqual(self.mock_rule, rule)
        self.assert_calls()

    def test_create_qos_bandwidth_limit_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.create_qos_bandwidth_limit_rule, self.policy_name,
            max_kbps=100)
        self.assert_calls()

    def test_create_qos_bandwidth_limit_rule_no_qos_direction_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'bandwidth_limit_rules']),
                 json={'bandwidth_limit_rule': self.mock_rule})
        ])
        rule = self.cloud.create_qos_bandwidth_limit_rule(
            self.policy_name, max_kbps=self.rule_max_kbps, direction="ingress")
        self.assertDictEqual(self.mock_rule, rule)
        self.assert_calls()

    def test_update_qos_bandwidth_limit_rule(self):
        expected_rule = copy.copy(self.mock_rule)
        expected_rule['max_kbps'] = self.rule_max_kbps + 100
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
                             'bandwidth_limit_rules',
                             '%s.json' % self.rule_id]),
                 json={'bandwidth_limit_rule': self.mock_rule}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'bandwidth_limit_rules',
                             '%s.json' % self.rule_id]),
                 json={'bandwidth_limit_rule': expected_rule},
                 validate=dict(
                     json={'bandwidth_limit_rule': {
                         'max_kbps': self.rule_max_kbps + 100}}))
        ])
        rule = self.cloud.update_qos_bandwidth_limit_rule(
            self.policy_id, self.rule_id, max_kbps=self.rule_max_kbps + 100)
        self.assertDictEqual(expected_rule, rule)
        self.assert_calls()

    def test_update_qos_bandwidth_limit_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.update_qos_bandwidth_limit_rule,
            self.policy_id, self.rule_id, max_kbps=2000)
        self.assert_calls()

    def test_update_qos_bandwidth_limit_rule_no_qos_direction_extension(self):
        expected_rule = copy.copy(self.mock_rule)
        expected_rule['direction'] = self.rule_max_kbps + 100
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies.json']),
                 json={'policies': [self.mock_policy]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'bandwidth_limit_rules',
                             '%s.json' % self.rule_id]),
                 json={'bandwidth_limit_rule': self.mock_rule}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'policies', self.policy_id,
                             'bandwidth_limit_rules',
                             '%s.json' % self.rule_id]),
                 json={'bandwidth_limit_rule': expected_rule},
                 validate=dict(
                     json={'bandwidth_limit_rule': {
                         'max_kbps': self.rule_max_kbps + 100}}))
        ])
        rule = self.cloud.update_qos_bandwidth_limit_rule(
            self.policy_id, self.rule_id, max_kbps=self.rule_max_kbps + 100,
            direction="ingress")
        # Even if there was attempt to change direction to 'ingress' it should
        # be not changed in returned rule
        self.assertDictEqual(expected_rule, rule)
        self.assert_calls()

    def test_delete_qos_bandwidth_limit_rule(self):
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
                             'bandwidth_limit_rules',
                             '%s.json' % self.rule_id]),
                 json={})
        ])
        self.assertTrue(
            self.cloud.delete_qos_bandwidth_limit_rule(
                self.policy_name, self.rule_id))
        self.assert_calls()

    def test_delete_qos_bandwidth_limit_rule_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.delete_qos_bandwidth_limit_rule,
            self.policy_name, self.rule_id)
        self.assert_calls()

    def test_delete_qos_bandwidth_limit_rule_not_found(self):
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
                             'bandwidth_limit_rules',
                             '%s.json' % self.rule_id]),
                 status_code=404)
        ])
        self.assertFalse(
            self.cloud.delete_qos_bandwidth_limit_rule(
                self.policy_name, self.rule_id))
        self.assert_calls()
