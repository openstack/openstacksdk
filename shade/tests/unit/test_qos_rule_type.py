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

from shade import exc
from shade.tests.unit import base


class TestQosRuleType(base.RequestsMockTestCase):

    qos_extension = {
        "updated": "2015-06-08T10:00:00-00:00",
        "name": "Quality of Service",
        "links": [],
        "alias": "qos",
        "description": "The Quality of Service extension."
    }

    mock_rule_type_bandwidth_limit = {
        'type': 'bandwidth_limit'
    }

    mock_rule_type_dscp_marking = {
        'type': 'dscp_marking'
    }

    mock_rule_types = [
        mock_rule_type_bandwidth_limit, mock_rule_type_dscp_marking]

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
