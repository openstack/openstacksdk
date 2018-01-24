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

from openstack.load_balancer import load_balancer_service as lb_service
from openstack import resource


class L7Rule(resource.Resource):
    resource_key = 'rule'
    resources_key = 'rules'
    base_path = '/v2.0/lbaas/l7policies/%(l7policy_id)s/rules'
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_update = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'compare_type', 'created_at', 'invert', 'key', 'project_id',
        'provisioning_status', 'type', 'updated_at', 'rule_value',
        'operating_status', is_admin_state_up='admin_state_up',
        l7_policy_id='l7policy_id',
    )

    #: Properties
    #: The administrative state of the l7policy *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: comparison type to be used with the value in this L7 rule.
    compare_type = resource.Body('compare_type')
    #: Timestamp when the L7 rule was created.
    created_at = resource.Body('created_at')
    #: inverts the logic of the rule if True
    #  (ie. perform a logical NOT on the rule)
    invert = resource.Body('invert', type=bool)
    #: The key to use for the comparison.
    key = resource.Body('key')
    #: The ID of the associated l7 policy
    l7_policy_id = resource.URI('l7policy_id')
    #: The operating status of this l7rule
    operating_status = resource.Body('operating_status')
    #: The ID of the project this l7policy is associated with.
    project_id = resource.Body('project_id')
    #: The provisioning status of this l7policy
    provisioning_status = resource.Body('provisioning_status')
    #: The type of L7 rule
    type = resource.Body('type')
    #: Timestamp when the L7 rule was updated.
    updated_at = resource.Body('updated_at')
    #: value to be compared with
    rule_value = resource.Body('value')
