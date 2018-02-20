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

from openstack.cloud import exc
from openstack.tests.unit import base


class TestQosRuleType(base.TestCase):

    rule_type_name = "bandwidth_limit"

    qos_extension = {
        "updated": "2015-06-08T10:00:00-00:00",
        "name": "Quality of Service",
        "links": [],
        "alias": "qos",
        "description": "The Quality of Service extension."
    }
    qos_rule_type_details_extension = {
        "updated": "2017-06-22T10:00:00-00:00",
        "name": "Details of QoS rule types",
        "links": [],
        "alias": "qos-rule-type-details",
        "description": ("Expose details about QoS rule types supported by "
                        "loaded backend drivers")
    }

    mock_rule_type_bandwidth_limit = {
        'type': 'bandwidth_limit'
    }
    mock_rule_type_dscp_marking = {
        'type': 'dscp_marking'
    }
    mock_rule_types = [
        mock_rule_type_bandwidth_limit, mock_rule_type_dscp_marking]

    mock_rule_type_details = {
        'drivers': [{
            'name': 'linuxbridge',
            'supported_parameters': [{
                'parameter_values': {'start': 0, 'end': 2147483647},
                'parameter_type': 'range',
                'parameter_name': u'max_kbps'
            }, {
                'parameter_values': ['ingress', 'egress'],
                'parameter_type': 'choices',
                'parameter_name': u'direction'
            }, {
                'parameter_values': {'start': 0, 'end': 2147483647},
                'parameter_type': 'range',
                'parameter_name': 'max_burst_kbps'
            }]
        }],
        'type': rule_type_name
    }

    def test_list_qos_rule_types(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'rule-types.json']),
                 json={'rule_types': self.mock_rule_types})
        ])
        rule_types = self.cloud.list_qos_rule_types()
        self.assertEqual(self.mock_rule_types, rule_types)
        self.assert_calls()

    def test_list_qos_rule_types_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_qos_rule_types)
        self.assert_calls()

    def test_get_qos_rule_type_details(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [
                     self.qos_extension,
                     self.qos_rule_type_details_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [
                     self.qos_extension,
                     self.qos_rule_type_details_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public',
                     append=['v2.0', 'qos', 'rule-types',
                             '%s.json' % self.rule_type_name]),
                     json={'rule_type': self.mock_rule_type_details})
        ])
        self.assertEqual(
            self.mock_rule_type_details,
            self.cloud.get_qos_rule_type_details(self.rule_type_name)
        )
        self.assert_calls()

    def test_get_qos_rule_type_details_no_qos_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': []})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.get_qos_rule_type_details, self.rule_type_name)
        self.assert_calls()

    def test_get_qos_rule_type_details_no_qos_details_extension(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'extensions.json']),
                 json={'extensions': [self.qos_extension]})
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.get_qos_rule_type_details, self.rule_type_name)
        self.assert_calls()
