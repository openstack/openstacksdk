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
from openstack import resource2 as resource
from openstack.auto_scaling import auto_scaling_service


class Instance(resource.Resource):
    resources_key = 'scaling_group_instances'
    base_path = '/scaling_group_instance'
    query_marker_key = 'start_number'
    next_marker_path = 'start_number'
    service = auto_scaling_service.AutoScalingService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'scaling_group_id', 'limit', 'health_status',
        lifecycle_state='life_cycle_state',
        marker=query_marker_key
    )

    #: Properties
    #: Valid values include ``private``, ``public``
    #: AutoScaling config ID
    id = resource.Body('instance_id')
    #: AutoScaling config name
    name = resource.Body('scaling_policy_name')
    #: valid values include: ``ALARM``, ``SCHEDULED``, ``RECURRENCE``
    type = resource.Body('scaling_policy_type')
    #: AutoScaling group reference the policy apply to
    scaling_group_id = resource.Body('scaling_group_id')
    alarm_id = resource.Body('alarm_id')
    scheduled_policy = resource.Body('scheduled_policy',
                                     type=ScheduledPolicy,
                                     default={})
    scaling_policy_action = resource.Body('scaling_policy_action',
                                          type=Action,
                                          default={})
    cool_down_time = resource.Body('cool_down_time')
    create_time = resource.Body('create_time')
    #: valid values include: ``INSERVICE``, ``PAUSED``
    status = resource.Body('policy_status')
