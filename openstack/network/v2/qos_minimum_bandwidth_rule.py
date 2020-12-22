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

from openstack import resource


class QoSMinimumBandwidthRule(resource.Resource):
    resource_key = 'minimum_bandwidth_rule'
    resources_key = 'minimum_bandwidth_rules'
    base_path = '/qos/policies/%(qos_policy_id)s/minimum_bandwidth_rules'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The ID of the QoS policy who owns rule.
    qos_policy_id = resource.URI('qos_policy_id')
    #: Minimum bandwidth in kbps.
    min_kbps = resource.Body('min_kbps')
    #: Traffic direction from the tenant point of view. Valid values: 'egress'
    direction = resource.Body('direction')
