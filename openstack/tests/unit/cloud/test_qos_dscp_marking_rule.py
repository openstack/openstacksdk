# Copyright 2017 OVH SAS
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
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

from openstack import exceptions
from openstack.network.v2 import qos_dscp_marking_rule
from openstack.tests.unit import base


class TestQosDscpMarkingRule(base.TestCase):
    policy_name = 'qos test policy'
    policy_id = '881d1bb7-a663-44c0-8f9f-ee2765b74486'
    project_id = 'c88fc89f-5121-4a4c-87fd-496b5af864e9'

    rule_id = 'ed1a2b05-0ad7-45d7-873f-008b575a02b3'
    rule_dscp_mark = 32

    mock_policy = {
        'id': policy_id,
        'name': policy_name,
        'description': '',
        'rules': [],
        'project_id': project_id,
        'tenant_id': project_id,
        'shared': False,
        'is_default': False,
    }

    mock_rule = {
        'id': rule_id,
        'dscp_mark': rule_dscp_mark,
    }

    qos_extension = {
        "updated": "2015-06-08T10:00:00-00:00",
        "name": "Quality of Service",
        "links": [],
        "alias": "qos",
        "description": "The Quality of Service extension.",
    }

    enabled_neutron_extensions = [qos_extension]

    def _compare_rules(self, exp, real):
        self.assertDictEqual(
            qos_dscp_marking_rule.QoSDSCPMarkingRule(**exp).to_dict(
                computed=False
            ),
            real.to_dict(computed=False),
        )

    def test_get_qos_dscp_marking_rule(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': self.enabled_neutron_extensions},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies', self.policy_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies'],
                        qs_elements=[f'name={self.policy_name}'],
                    ),
                    json={'policies': [self.mock_policy]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'qos',
                            'policies',
                            self.policy_id,
                            'dscp_marking_rules',
                            self.rule_id,
                        ],
                    ),
                    json={'dscp_marking_rule': self.mock_rule},
                ),
            ]
        )
        r = self.cloud.get_qos_dscp_marking_rule(
            self.policy_name, self.rule_id
        )
        self._compare_rules(self.mock_rule, r)
        self.assert_calls()

    def test_get_qos_dscp_marking_rule_no_qos_policy_found(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': self.enabled_neutron_extensions},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies', self.policy_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies'],
                        qs_elements=[f'name={self.policy_name}'],
                    ),
                    json={'policies': []},
                ),
            ]
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.cloud.get_qos_dscp_marking_rule,
            self.policy_name,
            self.rule_id,
        )
        self.assert_calls()

    def test_get_qos_dscp_marking_rule_no_qos_extension(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': []},
                )
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.get_qos_dscp_marking_rule,
            self.policy_name,
            self.rule_id,
        )
        self.assert_calls()

    def test_create_qos_dscp_marking_rule(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': self.enabled_neutron_extensions},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies', self.policy_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies'],
                        qs_elements=[f'name={self.policy_name}'],
                    ),
                    json={'policies': [self.mock_policy]},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'qos',
                            'policies',
                            self.policy_id,
                            'dscp_marking_rules',
                        ],
                    ),
                    json={'dscp_marking_rule': self.mock_rule},
                ),
            ]
        )
        rule = self.cloud.create_qos_dscp_marking_rule(
            self.policy_name, dscp_mark=self.rule_dscp_mark
        )
        self._compare_rules(self.mock_rule, rule)
        self.assert_calls()

    def test_create_qos_dscp_marking_rule_no_qos_extension(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': []},
                )
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_qos_dscp_marking_rule,
            self.policy_name,
            dscp_mark=16,
        )
        self.assert_calls()

    def test_update_qos_dscp_marking_rule(self):
        new_dscp_mark_value = 16
        expected_rule = copy.copy(self.mock_rule)
        expected_rule['dscp_mark'] = new_dscp_mark_value
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': self.enabled_neutron_extensions},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies', self.policy_id],
                    ),
                    json=self.mock_policy,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'qos',
                            'policies',
                            self.policy_id,
                            'dscp_marking_rules',
                            self.rule_id,
                        ],
                    ),
                    json={'dscp_marking_rule': self.mock_rule},
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'qos',
                            'policies',
                            self.policy_id,
                            'dscp_marking_rules',
                            self.rule_id,
                        ],
                    ),
                    json={'dscp_marking_rule': expected_rule},
                    validate=dict(
                        json={
                            'dscp_marking_rule': {
                                'dscp_mark': new_dscp_mark_value
                            }
                        }
                    ),
                ),
            ]
        )
        rule = self.cloud.update_qos_dscp_marking_rule(
            self.policy_id, self.rule_id, dscp_mark=new_dscp_mark_value
        )
        self._compare_rules(expected_rule, rule)
        self.assert_calls()

    def test_update_qos_dscp_marking_rule_no_qos_extension(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': []},
                )
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.update_qos_dscp_marking_rule,
            self.policy_id,
            self.rule_id,
            dscp_mark=8,
        )
        self.assert_calls()

    def test_delete_qos_dscp_marking_rule(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': self.enabled_neutron_extensions},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies', self.policy_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies'],
                        qs_elements=[f'name={self.policy_name}'],
                    ),
                    json={'policies': [self.mock_policy]},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'qos',
                            'policies',
                            self.policy_id,
                            'dscp_marking_rules',
                            self.rule_id,
                        ],
                    ),
                    json={},
                ),
            ]
        )
        self.assertTrue(
            self.cloud.delete_qos_dscp_marking_rule(
                self.policy_name, self.rule_id
            )
        )
        self.assert_calls()

    def test_delete_qos_dscp_marking_rule_no_qos_extension(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': []},
                )
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.delete_qos_dscp_marking_rule,
            self.policy_name,
            self.rule_id,
        )
        self.assert_calls()

    def test_delete_qos_dscp_marking_rule_not_found(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'extensions']
                    ),
                    json={'extensions': self.enabled_neutron_extensions},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies', self.policy_name],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'qos', 'policies'],
                        qs_elements=[f'name={self.policy_name}'],
                    ),
                    json={'policies': [self.mock_policy]},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'qos',
                            'policies',
                            self.policy_id,
                            'dscp_marking_rules',
                            self.rule_id,
                        ],
                    ),
                    status_code=404,
                ),
            ]
        )
        self.assertFalse(
            self.cloud.delete_qos_dscp_marking_rule(
                self.policy_name, self.rule_id
            )
        )
        self.assert_calls()
