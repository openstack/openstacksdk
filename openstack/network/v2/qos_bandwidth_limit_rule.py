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

from openstack.network import network_service
from openstack import resource


class QoSBandwidthLimitRule(resource.Resource):
    resource_key = 'bandwidth_limit_rule'
    resources_key = 'bandwidth_limit_rules'
    base_path = '/qos/policies/%(qos_policy_id)s/bandwidth_limit_rules'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: QoS bandwidth limit rule id.
    id = resource.prop('id')
    #: The ID of the QoS policy who owns rule.
    qos_policy_id = resource.prop('qos_policy_id')
    #: Maximum bandwidth in kbps.
    max_kbps = resource.prop('max_kbps')
    #: Maximum burst bandwidth in kbps.
    max_burst_kbps = resource.prop('max_burst_kbps')
    # NOTE(ralonsoh): to be implemented in bug 1560961
    #: Traffic direction from the tenant point of view ('egress', 'ingress').
    # direction = resource.prop('direction')

    @classmethod
    def _get_create_body(cls, attrs):
        # Exclude qos_policy_id from attrs since it is not expected by QoS API.
        if 'qos_policy_id' in attrs:
            attrs.pop('qos_policy_id')

        return {cls.resource_key: attrs}
